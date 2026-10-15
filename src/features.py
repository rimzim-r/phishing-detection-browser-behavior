URL_FEATURES = [
    "URLLength", "DomainLength", "IsDomainIP", "CharContinuationRate",
    "TLDLength", "NoOfSubDomain", "HasObfuscation", "NoOfObfuscatedChar",
    "ObfuscationRatio", "NoOfLettersInURL", "LetterRatioInURL",
    "NoOfDegitsInURL", "DegitRatioInURL", "NoOfEqualsInURL",
    "NoOfQMarkInURL", "NoOfAmpersandInURL", "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL", "IsHTTPS",
]

CONSISTENCY_FEATURES = [
    "HasTitle", "DomainTitleMatchScore", "URLTitleMatchScore", "HasFavicon",
    "HasDescription", "HasCopyrightInfo", "HasSocialNet",
    "NoOfSelfRef", "NoOfEmptyRef", "NoOfExternalRef",
]

BEHAVIOR_FEATURES = [
    "NoOfURLRedirect", "NoOfSelfRedirect", "NoOfPopup", "NoOfiFrame",
    "HasHiddenFields", "HasPasswordField", "HasSubmitButton",
    "HasExternalFormSubmit",
]

BASELINE = URL_FEATURES
HYBRID = URL_FEATURES + CONSISTENCY_FEATURES + BEHAVIOR_FEATURES
