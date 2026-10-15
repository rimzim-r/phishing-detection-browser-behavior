import re
from urllib.parse import urlparse


def extract_url_features(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    parts = domain.split(".")
    n = len(url)

    letters = sum(c.isalpha() for c in url)
    digits = sum(c.isdigit() for c in url)
    equals = url.count("=")
    qmark = url.count("?")
    amp = url.count("&")
    other = n - letters - digits - equals - qmark - amp

    return {
        "URLLength": n,
        "DomainLength": len(domain),
        "IsDomainIP": int(bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", domain))),
        "TLDLength": len(parts[-1]),
        "NoOfSubDomain": max(len(parts) - 2, 0),
        "NoOfLettersInURL": letters,
        "LetterRatioInURL": letters / n,
        "NoOfDegitsInURL": digits,
        "DegitRatioInURL": digits / n,
        "NoOfEqualsInURL": equals,
        "NoOfQMarkInURL": qmark,
        "NoOfAmpersandInURL": amp,
        "NoOfOtherSpecialCharsInURL": other,
        "SpacialCharRatioInURL": other / n,
        "IsHTTPS": int(parsed.scheme == "https"),
    }
