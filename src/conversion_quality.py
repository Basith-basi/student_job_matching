class ConversionQualityChecker:

    def compare(self, before_score, after_score):

        difference = after_score - before_score

        return {
            "before_score": before_score,
            "after_score": after_score,
            "difference": difference,
            "regression": difference < 0
        }