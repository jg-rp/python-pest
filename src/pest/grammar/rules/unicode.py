"""Built-in Unicode rules."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from pest.grammar.expression import RegexExpression
from pest.grammar.rule import SILENT
from pest.grammar.rule import BuiltInRule

if TYPE_CHECKING:
    from pest.grammar.expression import Expression


class UnicodePropertyRule(BuiltInRule):
    """Represents a built-in Unicode property rule."""

    __slots__ = ()

    def __init__(self, pattern: str, name: str):
        super().__init__(name, RegexExpression(pattern), SILENT)

    def __str__(self) -> str:
        return self.name

    def with_children(self, expressions: list[Expression]) -> Self:
        """Return a new instance of this expression with child expressions replaced."""
        assert len(expressions) == 1
        return self


def _make_registry(
    prop_type: str, mapping_or_list: dict[str, str] | list[str]
) -> dict[str, UnicodePropertyRule]:
    """Build registry of Unicode properties.

    Args:
        prop_type: "gc", "Binary", or "Script".
        mapping_or_list:
            - for "gc" or "Binary": dict {NAME_IN_PEST: UnicodePropertyValue}
            - for "Script": list of Unicode script names (CamelCase)
    """
    registry: dict[str, UnicodePropertyRule] = {}

    if prop_type in {"gc", "Binary"}:
        assert isinstance(mapping_or_list, dict)
        for key, value in mapping_or_list.items():
            registry[key] = UnicodePropertyRule(rf"\p{{{value}}}", key)

    elif prop_type == "Script":
        for script_name in mapping_or_list:
            key = script_name.upper().replace("-", "_")
            registry[key] = UnicodePropertyRule(rf"\p{{Script={script_name}}}", key)

    else:
        raise ValueError(f"Unknown property type: {prop_type}")

    return registry


GENERAL_CATEGORY_MAP = {
    "LETTER": "L",
    "CASED_LETTER": "LC",
    "UPPERCASE_LETTER": "Lu",
    "LOWERCASE_LETTER": "Ll",
    "TITLECASE_LETTER": "Lt",
    "MODIFIER_LETTER": "Lm",
    "OTHER_LETTER": "Lo",
    "MARK": "M",
    "NONSPACING_MARK": "Mn",
    "SPACING_MARK": "Mc",
    "ENCLOSING_MARK": "Me",
    "NUMBER": "N",
    "DECIMAL_NUMBER": "Nd",
    "LETTER_NUMBER": "Nl",
    "OTHER_NUMBER": "No",
    "PUNCTUATION": "P",
    "CONNECTOR_PUNCTUATION": "Pc",
    "DASH_PUNCTUATION": "Pd",
    "OPEN_PUNCTUATION": "Ps",
    "CLOSE_PUNCTUATION": "Pe",
    "INITIAL_PUNCTUATION": "Pi",
    "FINAL_PUNCTUATION": "Pf",
    "OTHER_PUNCTUATION": "Po",
    "SYMBOL": "S",
    "MATH_SYMBOL": "Sm",
    "CURRENCY_SYMBOL": "Sc",
    "MODIFIER_SYMBOL": "Sk",
    "OTHER_SYMBOL": "So",
    "SEPARATOR": "Z",
    "SPACE_SEPARATOR": "Zs",
    "LINE_SEPARATOR": "Zl",
    "PARAGRAPH_SEPARATOR": "Zp",
    "OTHER": "C",
    "CONTROL": "Cc",
    "FORMAT": "Cf",
    "SURROGATE": "Cs",
    "PRIVATE_USE": "Co",
    "UNASSIGNED": "Cn",
}


UNICODE_GENERAL_CATEGORY_RULES = _make_registry("gc", GENERAL_CATEGORY_MAP)

BINARY_PROPERTY_MAP = {
    "ALPHABETIC": "Alphabetic",
    "BIDI_CONTROL": "Bidi_Control",
    "BIDI_MIRRORED": "Bidi_Mirrored",
    "CASE_IGNORABLE": "Case_Ignorable",
    "CASED": "Cased",
    "CHANGES_WHEN_CASEFOLDED": "Changes_When_Casefolded",
    "CHANGES_WHEN_CASEMAPPED": "Changes_When_Casemapped",
    "CHANGES_WHEN_LOWERCASED": "Changes_When_Lowercased",
    "CHANGES_WHEN_TITLECASED": "Changes_When_Titlecased",
    "CHANGES_WHEN_UPPERCASED": "Changes_When_Uppercased",
    "DASH": "Dash",
    "DEFAULT_IGNORABLE_CODE_POINT": "Default_Ignorable_Code_Point",
    "DEPRECATED": "Deprecated",
    "DIACRITIC": "Diacritic",
    "EMOJI": "Emoji",
    "EMOJI_COMPONENT": "Emoji_Component",
    "EMOJI_MODIFIER": "Emoji_Modifier",
    "EMOJI_MODIFIER_BASE": "Emoji_Modifier_Base",
    "EMOJI_PRESENTATION": "Emoji_Presentation",
    "EXTENDED_PICTOGRAPHIC": "Extended_Pictographic",
    "EXTENDER": "Extender",
    "GRAPHEME_BASE": "Grapheme_Base",
    "GRAPHEME_EXTEND": "Grapheme_Extend",
    "GRAPHEME_LINK": "Grapheme_Link",
    "HEX_DIGIT": "Hex_Digit",
    "HYPHEN": "Hyphen",
    "IDS_BINARY_OPERATOR": "IDS_Binary_Operator",
    "IDS_TRINARY_OPERATOR": "IDS_Trinary_Operator",
    "ID_CONTINUE": "ID_Continue",
    "ID_START": "ID_Start",
    "IDEOGRAPHIC": "Ideographic",
    "JOIN_CONTROL": "Join_Control",
    "LOGICAL_ORDER_EXCEPTION": "Logical_Order_Exception",
    "LOWERCASE": "Lowercase",
    "MATH": "Math",
    "NONCHARACTER_CODE_POINT": "Noncharacter_Code_Point",
    "OTHER_ALPHABETIC": "Other_Alphabetic",
    "OTHER_DEFAULT_IGNORABLE_CODE_POINT": "Other_Default_Ignorable_Code_Point",
    "OTHER_GRAPHEME_EXTEND": "Other_Grapheme_Extend",
    "OTHER_ID_CONTINUE": "Other_ID_Continue",
    "OTHER_ID_START": "Other_ID_Start",
    "OTHER_LOWERCASE": "Other_Lowercase",
    "OTHER_MATH": "Other_Math",
    "OTHER_UPPERCASE": "Other_Uppercase",
    "PATTERN_SYNTAX": "Pattern_Syntax",
    "PATTERN_WHITE_SPACE": "Pattern_White_Space",
    "PREPENDED_CONCATENATION_MARK": "Prepended_Concatenation_Mark",
    "QUOTATION_MARK": "Quotation_Mark",
    "RADICAL": "Radical",
    "REGIONAL_INDICATOR": "Regional_Indicator",
    "SENTENCE_TERMINAL": "Sentence_Terminal",
    "SOFT_DOTTED": "Soft_Dotted",
    "TERMINAL_PUNCTUATION": "Terminal_Punctuation",
    "UNIFIED_IDEOGRAPH": "Unified_Ideograph",
    "UPPERCASE": "Uppercase",
    "VARIATION_SELECTOR": "Variation_Selector",
    "WHITE_SPACE": "White_Space",
    "XID_CONTINUE": "XID_Continue",
    "XID_START": "XID_Start",
}

UNICODE_BINARY_PROPERTY_RULES = _make_registry("Binary", BINARY_PROPERTY_MAP)

SCRIPT_NAMES = [
    "Adlam",
    "Ahom",
    "Anatolian_Hieroglyphs",
    "Arabic",
    "Armenian",
    "Avestan",
    "Balinese",
    "Bamum",
    "Bassa_Vah",
    "Batak",
    "Bengali",
    "Bhaiksuki",
    "Bopomofo",
    "Brahmi",
    "Braille",
    "Buginese",
    "Buhid",
    "Canadian_Aboriginal",
    "Carian",
    "Caucasian_Albanian",
    "Chakma",
    "Cham",
    "Cherokee",
    "Chorasmian",
    "Common",
    "Coptic",
    "Cuneiform",
    "Cypriot",
    "Cypro_Minoan",
    "Cyrillic",
    "Deseret",
    "Devanagari",
    "Dives_Akuru",
    "Dogra",
    "Duployan",
    "Egyptian_Hieroglyphs",
    "Elbasan",
    "Elymaic",
    "Ethiopic",
    "Georgian",
    "Glagolitic",
    "Gothic",
    "Grantha",
    "Greek",
    "Gujarati",
    "Gunjala_Gondi",
    "Gurmukhi",
    "Han",
    "Hangul",
    "Hanifi_Rohingya",
    "Hanunoo",
    "Hatran",
    "Hebrew",
    "Hiragana",
    "Imperial_Aramaic",
    "Inherited",
    "Inscriptional_Pahlavi",
    "Inscriptional_Parthian",
    "Javanese",
    "Kaithi",
    "Kannada",
    "Katakana",
    "Kawi",
    "Kayah_Li",
    "Kharoshthi",
    "Khitan_Small_Script",
    "Khmer",
    "Khojki",
    "Khudawadi",
    "Lao",
    "Latin",
    "Lepcha",
    "Limbu",
    "Linear_A",
    "Linear_B",
    "Lisu",
    "Lycian",
    "Lydian",
    "Mahajani",
    "Makasar",
    "Malayalam",
    "Mandaic",
    "Manichaean",
    "Marchen",
    "Masaram_Gondi",
    "Medefaidrin",
    "Meetei_Mayek",
    "Mende_Kikakui",
    "Meroitic_Cursive",
    "Meroitic_Hieroglyphs",
    "Miao",
    "Modi",
    "Mongolian",
    "Mro",
    "Multani",
    "Myanmar",
    "Nabataean",
    "Nag_Mundari",
    "Nandinagari",
    "New_Tai_Lue",
    "Newa",
    "Nko",
    "Nushu",
    "Nyiakeng_Puachue_Hmong",
    "Ogham",
    "Ol_Chiki",
    "Old_Hungarian",
    "Old_Italic",
    "Old_North_Arabian",
    "Old_Permic",
    "Old_Persian",
    "Old_Sogdian",
    "Old_South_Arabian",
    "Old_Turkic",
    "Old_Uyghur",
    "Oriya",
    "Osage",
    "Osmanya",
    "Pahawh_Hmong",
    "Palmyrene",
    "Pau_Cin_Hau",
    "Phags_Pa",
    "Phoenician",
    "Psalter_Pahlavi",
    "Rejang",
    "Runic",
    "Samaritan",
    "Saurashtra",
    "Sharada",
    "Shavian",
    "Siddham",
    "SignWriting",
    "Sinhala",
    "Sogdian",
    "Sora_Sompeng",
    "Soyombo",
    "Sundanese",
    "Syloti_Nagri",
    "Syriac",
    "Tagalog",
    "Tagbanwa",
    "Tai_Le",
    "Tai_Tham",
    "Tai_Viet",
    "Takri",
    "Tamil",
    "Tangsa",
    "Tangut",
    "Telugu",
    "Thaana",
    "Thai",
    "Tibetan",
    "Tifinagh",
    "Tirhuta",
    "Toto",
    "Ugaritic",
    "Vai",
    "Vithkuqi",
    "Wancho",
    "Warang_Citi",
    "Yezidi",
    "Yi",
    "Zanabazar_Square",
]

UNICODE_SCRIPT_PROPERTY_RULES = _make_registry("Script", SCRIPT_NAMES)

UNICODE_RULES = {
    **UNICODE_GENERAL_CATEGORY_RULES,
    **UNICODE_BINARY_PROPERTY_RULES,
    **UNICODE_SCRIPT_PROPERTY_RULES,
}
