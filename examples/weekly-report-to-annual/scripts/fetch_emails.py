#!/usr/bin/env python3
"""
Fetch weekly report emails from Feishu mailbox via IMAP.

Connects to Feishu IMAP server and retrieves emails with "周报" in the subject.
Supports both inbox and sent folders.
"""

import imaplib
import email
from email.header import decode_header
import json
import sys
from datetime import datetime


def decode_email_header(header):
    """Decode email header to readable string."""
    if header is None:
        return ""

    decoded_parts = []
    for part, encoding in decode_header(header):
        if isinstance(part, bytes):
            try:
                decoded_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except (LookupError, UnicodeDecodeError):
                decoded_parts.append(part.decode('utf-8', errors='ignore'))
        else:
            decoded_parts.append(part)

    return ''.join(decoded_parts)


def get_email_body(msg):
    """Extract email body from message."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    break
                except Exception:
                    continue
            elif content_type == "text/html" and "attachment" not in content_disposition and not body:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors='ignore')
                except Exception:
                    continue
    else:
        content_type = msg.get_content_type()
        if content_type in ["text/plain", "text/html"]:
            try:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='ignore')
            except Exception:
                body = str(msg.get_payload())

    return body


def list_folders(mail):
    """List all available folders."""
    status, folders = mail.list()
    folder_list = []
    if status == "OK":
        for folder in folders:
            # Parse folder name from response
            if isinstance(folder, bytes):
                folder = folder.decode('utf-8', errors='ignore')
            # Extract folder name (format: (\\flags) "delimiter" "name")
            if '"' in str(folder):
                parts = str(folder).split('"')
                if len(parts) >= 3:
                    folder_list.append(parts[-2])
    return folder_list


def search_in_folder(mail, folder_name, search_keyword, max_emails, year_filter=None):
    """Search for emails in a specific folder."""
    weekly_reports = []

    try:
        # Try to select the folder
        status, _ = mail.select(folder_name)
        if status != "OK":
            return weekly_reports, f"Cannot select folder: {folder_name}"
    except Exception as e:
        return weekly_reports, str(e)

    # Search for all emails first, then filter by keyword
    try:
        status, messages = mail.search(None, "ALL")
    except Exception as e:
        return weekly_reports, str(e)

    if status != "OK":
        return weekly_reports, "Search failed"

    email_ids = messages[0].split()

    # Get most recent emails (reversed order)
    email_ids = email_ids[-max_emails:] if len(email_ids) > max_emails else email_ids
    email_ids = list(reversed(email_ids))  # Most recent first

    for email_id in email_ids:
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject = decode_email_header(msg["Subject"])

                    # Filter by keyword
                    if search_keyword not in subject:
                        continue

                    sender = decode_email_header(msg["From"])
                    to = decode_email_header(msg["To"])
                    date_str = msg["Date"]
                    body = get_email_body(msg)

                    # Parse date
                    date_formatted = date_str
                    try:
                        for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z"]:
                            try:
                                date_obj = datetime.strptime(date_str.strip(), fmt)
                                date_formatted = date_obj.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass

                    # 年份过滤
                    if year_filter:
                        try:
                            email_year = int(date_formatted[:4])
                            if email_year != year_filter:
                                continue
                        except (ValueError, IndexError):
                            pass  # 无法解析日期时不过滤

                    weekly_reports.append({
                        "subject": subject,
                        "sender": sender,
                        "to": to,
                        "date": date_formatted,
                        "folder": folder_name,
                        "body": body[:5000],  # Limit body size
                    })
        except Exception:
            continue

    return weekly_reports, None


def main():
    """Main entry point."""
    stdin_content = sys.stdin.read().strip()

    try:
        input_data = json.loads(stdin_content)
        email_addr = input_data.get("email", "")
        password = input_data.get("password", "")
        imap_server = input_data.get("imap_server", "imap.feishu.cn")
        imap_port = input_data.get("imap_port", 993)
        search_keyword = input_data.get("search_keyword", "周报")
        max_emails = input_data.get("max_emails", 52)
        # 搜索所有文件夹，或指定文件夹
        folders = input_data.get("folders", None)  # None 表示搜索所有文件夹
        # 年份过滤，只获取指定年份的邮件
        year_filter = input_data.get("year", 2025)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}, ensure_ascii=False))
        return

    if not email_addr or not password:
        print(json.dumps({
            "error": "Email and password are required",
            "hint": "Please provide 'email' and 'password' in the input JSON"
        }, ensure_ascii=False))
        return

    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_addr, password)

        # List all available folders
        available_folders = list_folders(mail)

        weekly_reports = []
        searched_folders = []
        errors = []

        # 如果没有指定文件夹，搜索所有文件夹
        folders_to_search = folders if folders else available_folders

        # Search in folders
        for folder in folders_to_search:
            # Check if folder exists (case-insensitive match)
            matched_folder = None
            for af in available_folders:
                if folder.lower() == af.lower() or folder in af or af in folder:
                    matched_folder = af
                    break

            if matched_folder and matched_folder not in searched_folders:
                reports, error = search_in_folder(mail, matched_folder, search_keyword, max_emails, year_filter)
                searched_folders.append(matched_folder)
                if error:
                    errors.append(f"{matched_folder}: {error}")
                weekly_reports.extend(reports)

        mail.logout()

        # Sort by date (most recent first)
        weekly_reports.sort(key=lambda x: x.get("date", ""), reverse=True)

        # Remove duplicates based on subject and date
        seen = set()
        unique_reports = []
        for report in weekly_reports:
            key = (report.get("subject", ""), report.get("date", ""))
            if key not in seen:
                seen.add(key)
                unique_reports.append(report)

        result = {
            "status": "success",
            "email": email_addr,
            "imap_server": imap_server,
            "search_keyword": search_keyword,
            "year_filter": year_filter,
            "available_folders": available_folders,
            "searched_folders": searched_folders,
            "total_found": len(unique_reports),
            "emails": unique_reports,
        }

        if errors:
            result["warnings"] = errors

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except imaplib.IMAP4.error as e:
        print(json.dumps({
            "error": f"IMAP error: {str(e)}",
            "hint": "Please check your email, password, and IMAP server settings"
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
