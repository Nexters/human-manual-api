from pakit.services.result_content import EMOTIONAL_PROCESSING_COPY, FeatureCopy


def build_emotional_processing_feature(expression: int, egen: int) -> FeatureCopy:
    expression_pole = "direct" if expression >= 50 else "explore"
    egen_pole = "egen" if egen >= 50 else "teto"
    return EMOTIONAL_PROCESSING_COPY[(expression_pole, egen_pole)]
