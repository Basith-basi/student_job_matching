class RetryService:

    def retry(self, attempts):

        if attempts < 3:
            return True

        return False