

def get_git_primary_email(emails: list[dict]):
    for email in emails:
        if email['primary']:
            return email['email']