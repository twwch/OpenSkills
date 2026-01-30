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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


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


def search_in_folder_with_connection(folder_name, email_addr, password, imap_server, imap_port,
                                    search_keyword, max_emails, year_filter=None):
    """Search for emails in a specific folder with its own IMAP connection."""
    weekly_reports = []

    try:
        # Each thread creates its own connection
        print(f"[DEBUG] [线程] 为文件夹 {folder_name} 创建连接...", file=sys.stderr)
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_addr, password)

        # Search in the folder
        reports, error = search_in_folder(mail, folder_name, search_keyword, max_emails, year_filter)

        # Close connection
        mail.logout()
        print(f"[DEBUG] [线程] 文件夹 {folder_name} 搜索完成，找到 {len(reports)} 封邮件", file=sys.stderr)

        return folder_name, reports, error
    except Exception as e:
        print(f"[DEBUG] [线程] 文件夹 {folder_name} 搜索失败: {str(e)}", file=sys.stderr)
        return folder_name, [], str(e)


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
        print(f"[DEBUG]   正在搜索文件夹中的邮件...", file=sys.stderr)
        status, messages = mail.search(None, "ALL")
        print(f"[DEBUG]   搜索完成", file=sys.stderr)
    except Exception as e:
        return weekly_reports, str(e)

    if status != "OK":
        return weekly_reports, "Search failed"

    email_ids = messages[0].split()
    print(f"[DEBUG]   找到 {len(email_ids)} 封邮件，准备获取最近 {max_emails} 封", file=sys.stderr)

    # Get most recent emails (reversed order)
    email_ids = email_ids[-max_emails:] if len(email_ids) > max_emails else email_ids
    email_ids = list(reversed(email_ids))  # Most recent first

    for idx, email_id in enumerate(email_ids, 1):
        if idx % 10 == 0:  # 每处理10封邮件打印一次进度
            print(f"[DEBUG]   已处理 {idx}/{len(email_ids)} 封邮件", file=sys.stderr)
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
        print(f"[DEBUG] 正在连接 IMAP 服务器: {imap_server}:{imap_port}", file=sys.stderr)
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        print(f"[DEBUG] 连接成功，正在登录...", file=sys.stderr)
        mail.login(email_addr, password)
        print(f"[DEBUG] 登录成功", file=sys.stderr)

        # List all available folders
        print(f"[DEBUG] 正在列出所有文件夹...", file=sys.stderr)
        available_folders = list_folders(mail)
        print(f"[DEBUG] 找到 {len(available_folders)} 个文件夹: {available_folders}", file=sys.stderr)

        weekly_reports = []
        searched_folders = []
        errors = []

        # 如果没有指定文件夹，搜索所有文件夹
        folders_to_search = folders if folders else available_folders

        # Match folders (case-insensitive)
        matched_folders = []
        for folder in folders_to_search:
            for af in available_folders:
                if folder.lower() == af.lower() or folder in af or af in folder:
                    if af not in matched_folders:
                        matched_folders.append(af)
                    break

        # Close the initial connection, each thread will create its own
        mail.logout()
        print(f"[DEBUG] 初始连接已关闭", file=sys.stderr)

        # Search folders concurrently
        print(f"[DEBUG] 使用并发方式搜索 {len(matched_folders)} 个文件夹 (最多5个并发)", file=sys.stderr)

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_folder = {
                executor.submit(
                    search_in_folder_with_connection,
                    folder,
                    email_addr,
                    password,
                    imap_server,
                    imap_port,
                    search_keyword,
                    max_emails,
                    year_filter
                ): folder
                for folder in matched_folders
            }

            # Collect results as they complete
            for future in as_completed(future_to_folder):
                folder_name, reports, error = future.result()
                searched_folders.append(folder_name)
                if error:
                    errors.append(f"{folder_name}: {error}")
                weekly_reports.extend(reports)

        print(f"[DEBUG] 所有文件夹搜索完成", file=sys.stderr)

        # Sort by date (most recent first)
        print(f"[DEBUG] 正在排序和去重 {len(weekly_reports)} 封邮件...", file=sys.stderr)
        weekly_reports.sort(key=lambda x: x.get("date", ""), reverse=True)

        # Remove duplicates based on subject and date
        seen = set()
        unique_reports = []
        for report in weekly_reports:
            key = (report.get("subject", ""), report.get("date", ""))
            if key not in seen:
                seen.add(key)
                unique_reports.append(report)
        print(f"[DEBUG] 去重后剩余 {len(unique_reports)} 封邮件", file=sys.stderr)

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
