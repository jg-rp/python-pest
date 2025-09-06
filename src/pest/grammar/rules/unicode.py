class UnicodePropertyRule:
    """Generic Unicode property rule."""

    def __init__(self, pattern: str, name: str):
        self.pattern = pattern
        self.name = name

    def __str__(self) -> str:
        return self.name


class Letter(UnicodePropertyRule):
    """Unicode category: Letter (L)."""

    PATTERN = r"\p{L}"

    def __str__(self) -> str:
        return "LETTER"


class CasedLetter(UnicodePropertyRule):
    """Unicode category: Cased Letter (LC)."""

    PATTERN = r"\p{LC}"

    def __str__(self) -> str:
        return "CASED_LETTER"


class UppercaseLetter(UnicodePropertyRule):
    """Unicode category: Uppercase Letter (Lu)."""

    PATTERN = r"\p{Lu}"

    def __str__(self) -> str:
        return "UPPERCASE_LETTER"


class LowercaseLetter(UnicodePropertyRule):
    """Unicode category: Lowercase Letter (Ll)."""

    PATTERN = r"\p{Ll}"

    def __str__(self) -> str:
        return "LOWERCASE_LETTER"


class TitleCaseLetter(UnicodePropertyRule):
    """Unicode category: TitleCase Letter (Lt)."""

    PATTERN = r"\p{Lt}"

    def __str__(self) -> str:
        return "TITLECASE_LETTER"


class ModifierLetter(UnicodePropertyRule):
    """Unicode category: Modifier Letter (Lm)."""

    PATTERN = r"\p{Lm}"

    def __str__(self) -> str:
        return "MODIFIER_LETTER"


class OtherLetter(UnicodePropertyRule):
    """Unicode category: Other Letter (Lo)."""

    PATTERN = r"\p{Lo}"

    def __str__(self) -> str:
        return "OTHER_LETTER"


class Mark(UnicodePropertyRule):
    """Unicode category: Mark (M)."""

    PATTERN = r"\p{M}"

    def __str__(self) -> str:
        return "MARK"


class NonspacingMark(UnicodePropertyRule):
    """Unicode category: Nonspacing Mark (Mn)."""

    PATTERN = r"\p{Mn}"

    def __str__(self) -> str:
        return "NONSPACING_MARK"


class SpacingMark(UnicodePropertyRule):
    """Unicode category: Spacing Mark (Mc)."""

    PATTERN = r"\p{Mc}"

    def __str__(self) -> str:
        return "SPACING_MARK"


class EnclosingMark(UnicodePropertyRule):
    """Unicode category: Enclosing Mark (Me)."""

    PATTERN = r"\p{Me}"

    def __str__(self) -> str:
        return "ENCLOSING_MARK"


class Number(UnicodePropertyRule):
    """Unicode category: Number (N)."""

    PATTERN = r"\p{N}"

    def __str__(self) -> str:
        return "NUMBER"


class DecimalNumber(UnicodePropertyRule):
    """Unicode category: Decimal Number (Nd)."""

    PATTERN = r"\p{Nd}"

    def __str__(self) -> str:
        return "DECIMAL_NUMBER"


class LetterNumber(UnicodePropertyRule):
    """Unicode category: Letter Number (Nl)."""

    PATTERN = r"\p{Nl}"

    def __str__(self) -> str:
        return "LETTER_NUMBER"


class OtherNumber(UnicodePropertyRule):
    """Unicode category: Other Number (No)."""

    PATTERN = r"\p{No}"

    def __str__(self) -> str:
        return "OTHER_NUMBER"


class Punctuation(UnicodePropertyRule):
    """Unicode category: Punctuation (P)."""

    PATTERN = r"\p{P}"

    def __str__(self) -> str:
        return "PUNCTUATION"


class ConnectorPunctuation(UnicodePropertyRule):
    """Unicode category: Connector Punctuation (Pc)."""

    PATTERN = r"\p{Pc}"

    def __str__(self) -> str:
        return "CONNECTOR_PUNCTUATION"


class DashPunctuation(UnicodePropertyRule):
    """Unicode category: Dash Punctuation (Pd)."""

    PATTERN = r"\p{Pd}"

    def __str__(self) -> str:
        return "DASH_PUNCTUATION"


class OpenPunctuation(UnicodePropertyRule):
    """Unicode category: Open Punctuation (Ps)."""

    PATTERN = r"\p{Ps}"

    def __str__(self) -> str:
        return "OPEN_PUNCTUATION"


class ClosePunctuation(UnicodePropertyRule):
    """Unicode category: Close Punctuation (Pe)."""

    PATTERN = r"\p{Pe}"

    def __str__(self) -> str:
        return "CLOSE_PUNCTUATION"


class InitialPunctuation(UnicodePropertyRule):
    """Unicode category: Initial Punctuation (Pi)."""

    PATTERN = r"\p{Pi}"

    def __str__(self) -> str:
        return "INITIAL_PUNCTUATION"


class FinalPunctuation(UnicodePropertyRule):
    """Unicode category: Final Punctuation (Pf)."""

    PATTERN = r"\p{Pf}"

    def __str__(self) -> str:
        return "FINAL_PUNCTUATION"


class OtherPunctuation(UnicodePropertyRule):
    """Unicode category: Other Punctuation (Po)."""

    PATTERN = r"\p{Po}"

    def __str__(self) -> str:
        return "OTHER_PUNCTUATION"


class Symbol(UnicodePropertyRule):
    """Unicode category: Symbol (S)."""

    PATTERN = r"\p{S}"

    def __str__(self) -> str:
        return "SYMBOL"


class MathSymbol(UnicodePropertyRule):
    """Unicode category: Math Symbol (Sm)."""

    PATTERN = r"\p{Sm}"

    def __str__(self) -> str:
        return "MATH_SYMBOL"


class CurrencySymbol(UnicodePropertyRule):
    """Unicode category: Currency Symbol (Sc)."""

    PATTERN = r"\p{Sc}"

    def __str__(self) -> str:
        return "CURRENCY_SYMBOL"


class ModifierSymbol(UnicodePropertyRule):
    """Unicode category: Modifier Symbol (Sk)."""

    PATTERN = r"\p{Sk}"

    def __str__(self) -> str:
        return "MODIFIER_SYMBOL"


class OtherSymbol(UnicodePropertyRule):
    """Unicode category: Other Symbol (So)."""

    PATTERN = r"\p{So}"

    def __str__(self) -> str:
        return "OTHER_SYMBOL"


class Separator(UnicodePropertyRule):
    """Unicode category: Separator (Z)."""

    PATTERN = r"\p{Z}"

    def __str__(self) -> str:
        return "SEPARATOR"


class SpaceSeparator(UnicodePropertyRule):
    """Unicode category: Space Separator (Zs)."""

    PATTERN = r"\p{Zs}"

    def __str__(self) -> str:
        return "SPACE_SEPARATOR"


class LineSeparator(UnicodePropertyRule):
    """Unicode category: Line Separator (Zl)."""

    PATTERN = r"\p{Zl}"

    def __str__(self) -> str:
        return "LINE_SEPARATOR"


class ParagraphSeparator(UnicodePropertyRule):
    """Unicode category: Paragraph Separator (Zp)."""

    PATTERN = r"\p{Zp}"

    def __str__(self) -> str:
        return "PARAGRAPH_SEPARATOR"


class Other(UnicodePropertyRule):
    """Unicode category: Other (C)."""

    PATTERN = r"\p{C}"

    def __str__(self) -> str:
        return "OTHER"


class Control(UnicodePropertyRule):
    """Unicode category: Control (Cc)."""

    PATTERN = r"\p{Cc}"

    def __str__(self) -> str:
        return "CONTROL"


class Format(UnicodePropertyRule):
    """Unicode category: Format (Cf)."""

    PATTERN = r"\p{Cf}"

    def __str__(self) -> str:
        return "FORMAT"


class Surrogate(UnicodePropertyRule):
    """Unicode category: Surrogate (Cs)."""

    PATTERN = r"\p{Cs}"

    def __str__(self) -> str:
        return "SURROGATE"


class PrivateUse(UnicodePropertyRule):
    """Unicode category: Private Use (Co)."""

    PATTERN = r"\p{Co}"

    def __str__(self) -> str:
        return "PRIVATE_USE"


class Unassigned(UnicodePropertyRule):
    """Unicode category: Unassigned (Cn)."""

    PATTERN = r"\p{Cn}"

    def __str__(self) -> str:
        return "UNASSIGNED"


# === Binary Property Rules ===


class Alphabetic(UnicodePropertyRule):
    PATTERN = r"\p{Alphabetic}"

    def __str__(self) -> str:
        return "ALPHABETIC"


class BidiControl(UnicodePropertyRule):
    PATTERN = r"\p{Bidi_Control}"

    def __str__(self) -> str:
        return "BIDI_CONTROL"


class BidiMirrored(UnicodePropertyRule):
    PATTERN = r"\p{Bidi_Mirrored}"

    def __str__(self) -> str:
        return "BIDI_MIRRORED"


class CaseIgnorable(UnicodePropertyRule):
    PATTERN = r"\p{Case_Ignorable}"

    def __str__(self) -> str:
        return "CASE_IGNORABLE"


class Cased(UnicodePropertyRule):
    PATTERN = r"\p{Cased}"

    def __str__(self) -> str:
        return "CASED"


class ChangesWhenCasefolded(UnicodePropertyRule):
    PATTERN = r"\p{Changes_When_Casefolded}"

    def __str__(self) -> str:
        return "CHANGES_WHEN_CASEFOLDED"


class ChangesWhenCasemapped(UnicodePropertyRule):
    PATTERN = r"\p{Changes_When_Casemapped}"

    def __str__(self) -> str:
        return "CHANGES_WHEN_CASEMAPPED"


class ChangesWhenLowercased(UnicodePropertyRule):
    PATTERN = r"\p{Changes_When_Lowercased}"

    def __str__(self) -> str:
        return "CHANGES_WHEN_LOWERCASED"


class ChangesWhenTitlecased(UnicodePropertyRule):
    PATTERN = r"\p{Changes_When_Titlecased}"

    def __str__(self) -> str:
        return "CHANGES_WHEN_TITLECASED"


class ChangesWhenUppercased(UnicodePropertyRule):
    PATTERN = r"\p{Changes_When_Uppercased}"

    def __str__(self) -> str:
        return "CHANGES_WHEN_UPPERCASED"


class Dash(UnicodePropertyRule):
    PATTERN = r"\p{Dash}"

    def __str__(self) -> str:
        return "DASH"


class DefaultIgnorableCodePoint(UnicodePropertyRule):
    PATTERN = r"\p{Default_Ignorable_Code_Point}"

    def __str__(self) -> str:
        return "DEFAULT_IGNORABLE_CODE_POINT"


class Deprecated(UnicodePropertyRule):
    PATTERN = r"\p{Deprecated}"

    def __str__(self) -> str:
        return "DEPRECATED"


class Diacritic(UnicodePropertyRule):
    PATTERN = r"\p{Diacritic}"

    def __str__(self) -> str:
        return "DIACRITIC"


class Emoji(UnicodePropertyRule):
    PATTERN = r"\p{Emoji}"

    def __str__(self) -> str:
        return "EMOJI"


class EmojiComponent(UnicodePropertyRule):
    PATTERN = r"\p{Emoji_Component}"

    def __str__(self) -> str:
        return "EMOJI_COMPONENT"


class EmojiModifier(UnicodePropertyRule):
    PATTERN = r"\p{Emoji_Modifier}"

    def __str__(self) -> str:
        return "EMOJI_MODIFIER"


class EmojiModifierBase(UnicodePropertyRule):
    PATTERN = r"\p{Emoji_Modifier_Base}"

    def __str__(self) -> str:
        return "EMOJI_MODIFIER_BASE"


class EmojiPresentation(UnicodePropertyRule):
    PATTERN = r"\p{Emoji_Presentation}"

    def __str__(self) -> str:
        return "EMOJI_PRESENTATION"


class ExtendedPictographic(UnicodePropertyRule):
    PATTERN = r"\p{Extended_Pictographic}"

    def __str__(self) -> str:
        return "EXTENDED_PICTOGRAPHIC"


class Extender(UnicodePropertyRule):
    PATTERN = r"\p{Extender}"

    def __str__(self) -> str:
        return "EXTENDER"


class GraphemeBase(UnicodePropertyRule):
    PATTERN = r"\p{Grapheme_Base}"

    def __str__(self) -> str:
        return "GRAPHEME_BASE"


class GraphemeExtend(UnicodePropertyRule):
    PATTERN = r"\p{Grapheme_Extend}"

    def __str__(self) -> str:
        return "GRAPHEME_EXTEND"


class GraphemeLink(UnicodePropertyRule):
    PATTERN = r"\p{Grapheme_Link}"

    def __str__(self) -> str:
        return "GRAPHEME_LINK"


class HexDigit(UnicodePropertyRule):
    PATTERN = r"\p{Hex_Digit}"

    def __str__(self) -> str:
        return "HEX_DIGIT"


class Hyphen(UnicodePropertyRule):
    PATTERN = r"\p{Hyphen}"

    def __str__(self) -> str:
        return "HYPHEN"


class IdsBinaryOperator(UnicodePropertyRule):
    PATTERN = r"\p{IDS_Binary_Operator}"

    def __str__(self) -> str:
        return "IDS_BINARY_OPERATOR"


class IdsTrinaryOperator(UnicodePropertyRule):
    PATTERN = r"\p{IDS_Trinary_Operator}"

    def __str__(self) -> str:
        return "IDS_TRINARY_OPERATOR"


class IdContinue(UnicodePropertyRule):
    PATTERN = r"\p{ID_Continue}"

    def __str__(self) -> str:
        return "ID_CONTINUE"


class IdStart(UnicodePropertyRule):
    PATTERN = r"\p{ID_Start}"

    def __str__(self) -> str:
        return "ID_START"


class Ideographic(UnicodePropertyRule):
    PATTERN = r"\p{Ideographic}"

    def __str__(self) -> str:
        return "IDEOGRAPHIC"


class JoinControl(UnicodePropertyRule):
    PATTERN = r"\p{Join_Control}"

    def __str__(self) -> str:
        return "JOIN_CONTROL"


class LogicalOrderException(UnicodePropertyRule):
    PATTERN = r"\p{Logical_Order_Exception}"

    def __str__(self) -> str:
        return "LOGICAL_ORDER_EXCEPTION"


class Lowercase(UnicodePropertyRule):
    PATTERN = r"\p{Lowercase}"

    def __str__(self) -> str:
        return "LOWERCASE"


class Math(UnicodePropertyRule):
    PATTERN = r"\p{Math}"

    def __str__(self) -> str:
        return "MATH"


class NoncharacterCodePoint(UnicodePropertyRule):
    PATTERN = r"\p{Noncharacter_Code_Point}"

    def __str__(self) -> str:
        return "NONCHARACTER_CODE_POINT"


class OtherAlphabetic(UnicodePropertyRule):
    PATTERN = r"\p{Other_Alphabetic}"

    def __str__(self) -> str:
        return "OTHER_ALPHABETIC"


class OtherDefaultIgnorableCodePoint(UnicodePropertyRule):
    PATTERN = r"\p{Other_Default_Ignorable_Code_Point}"

    def __str__(self) -> str:
        return "OTHER_DEFAULT_IGNORABLE_CODE_POINT"


class OtherGraphemeExtend(UnicodePropertyRule):
    PATTERN = r"\p{Other_Grapheme_Extend}"

    def __str__(self) -> str:
        return "OTHER_GRAPHEME_EXTEND"


class OtherIdContinue(UnicodePropertyRule):
    PATTERN = r"\p{Other_ID_Continue}"

    def __str__(self) -> str:
        return "OTHER_ID_CONTINUE"


class OtherIdStart(UnicodePropertyRule):
    PATTERN = r"\p{Other_ID_Start}"

    def __str__(self) -> str:
        return "OTHER_ID_START"


class OtherLowercase(UnicodePropertyRule):
    PATTERN = r"\p{Other_Lowercase}"

    def __str__(self) -> str:
        return "OTHER_LOWERCASE"


class OtherMath(UnicodePropertyRule):
    PATTERN = r"\p{Other_Math}"

    def __str__(self) -> str:
        return "OTHER_MATH"


class OtherUppercase(UnicodePropertyRule):
    PATTERN = r"\p{Other_Uppercase}"

    def __str__(self) -> str:
        return "OTHER_UPPERCASE"


class PatternSyntax(UnicodePropertyRule):
    PATTERN = r"\p{Pattern_Syntax}"

    def __str__(self) -> str:
        return "PATTERN_SYNTAX"


class PatternWhiteSpace(UnicodePropertyRule):
    PATTERN = r"\p{Pattern_White_Space}"

    def __str__(self) -> str:
        return "PATTERN_WHITE_SPACE"


class PrependedConcatenationMark(UnicodePropertyRule):
    PATTERN = r"\p{Prepended_Concatenation_Mark}"

    def __str__(self) -> str:
        return "PREPENDED_CONCATENATION_MARK"


class QuotationMark(UnicodePropertyRule):
    PATTERN = r"\p{Quotation_Mark}"

    def __str__(self) -> str:
        return "QUOTATION_MARK"


class Radical(UnicodePropertyRule):
    PATTERN = r"\p{Radical}"

    def __str__(self) -> str:
        return "RADICAL"


class RegionalIndicator(UnicodePropertyRule):
    PATTERN = r"\p{Regional_Indicator}"

    def __str__(self) -> str:
        return "REGIONAL_INDICATOR"


class SentenceTerminal(UnicodePropertyRule):
    PATTERN = r"\p{Sentence_Terminal}"

    def __str__(self) -> str:
        return "SENTENCE_TERMINAL"


class SoftDotted(UnicodePropertyRule):
    PATTERN = r"\p{Soft_Dotted}"

    def __str__(self) -> str:
        return "SOFT_DOTTED"


class TerminalPunctuation(UnicodePropertyRule):
    PATTERN = r"\p{Terminal_Punctuation}"

    def __str__(self) -> str:
        return "TERMINAL_PUNCTUATION"


class UnifiedIdeograph(UnicodePropertyRule):
    PATTERN = r"\p{Unified_Ideograph}"

    def __str__(self) -> str:
        return "UNIFIED_IDEOGRAPH"


class Uppercase(UnicodePropertyRule):
    PATTERN = r"\p{Uppercase}"

    def __str__(self) -> str:
        return "UPPERCASE"


class VariationSelector(UnicodePropertyRule):
    PATTERN = r"\p{Variation_Selector}"

    def __str__(self) -> str:
        return "VARIATION_SELECTOR"


class WhiteSpace(UnicodePropertyRule):
    PATTERN = r"\p{White_Space}"

    def __str__(self) -> str:
        return "WHITE_SPACE"


class XidContinue(UnicodePropertyRule):
    PATTERN = r"\p{XID_Continue}"

    def __str__(self) -> str:
        return "XID_CONTINUE"


class XidStart(UnicodePropertyRule):
    PATTERN = r"\p{XID_Start}"

    def __str__(self) -> str:
        return "XID_START"


# UNICODE_PROPERTY_RULES = {
#     "LETTER": Letter(),
#     "CASED_LETTER": CasedLetter(),
#     "UPPERCASE_LETTER": UppercaseLetter(),
#     "LOWERCASE_LETTER": LowercaseLetter(),
#     "TITLECASE_LETTER": TitleCaseLetter(),
#     "MODIFIER_LETTER": ModifierLetter(),
#     "OTHER_LETTER": OtherLetter(),
#     "MARK": Mark(),
#     "NONSPACING_MARK": NonspacingMark(),
#     "SPACING_MARK": SpacingMark(),
#     "ENCLOSING_MARK": EnclosingMark(),
#     "NUMBER": Number(),
#     "DECIMAL_NUMBER": DecimalNumber(),
#     "LETTER_NUMBER": LetterNumber(),
#     "OTHER_NUMBER": OtherNumber(),
#     "PUNCTUATION": Punctuation(),
#     "CONNECTOR_PUNCTUATION": ConnectorPunctuation(),
#     "DASH_PUNCTUATION": DashPunctuation(),
#     "OPEN_PUNCTUATION": OpenPunctuation(),
#     "CLOSE_PUNCTUATION": ClosePunctuation(),
#     "INITIAL_PUNCTUATION": InitialPunctuation(),
#     "FINAL_PUNCTUATION": FinalPunctuation(),
#     "OTHER_PUNCTUATION": OtherPunctuation(),
#     "SYMBOL": Symbol(),
#     "MATH_SYMBOL": MathSymbol(),
#     "CURRENCY_SYMBOL": CurrencySymbol(),
#     "MODIFIER_SYMBOL": ModifierSymbol(),
#     "OTHER_SYMBOL": OtherSymbol(),
#     "SEPARATOR": Separator(),
#     "SPACE_SEPARATOR": SpaceSeparator(),
#     "LINE_SEPARATOR": LineSeparator(),
#     "PARAGRAPH_SEPARATOR": ParagraphSeparator(),
#     "OTHER": Other(),
#     "CONTROL": Control(),
#     "FORMAT": Format(),
#     "SURROGATE": Surrogate(),
#     "PRIVATE_USE": PrivateUse(),
#     "UNASSIGNED": Unassigned(),
# }


# UNICODE_BINARY_PROPERTY_RULES = {
#     "ALPHABETIC": Alphabetic(),
#     "BIDI_CONTROL": BidiControl(),
#     "BIDI_MIRRORED": BidiMirrored(),
#     "CASE_IGNORABLE": CaseIgnorable(),
#     "CASED": Cased(),
#     "CHANGES_WHEN_CASEFOLDED": ChangesWhenCasefolded(),
#     "CHANGES_WHEN_CASEMAPPED": ChangesWhenCasemapped(),
#     "CHANGES_WHEN_LOWERCASED": ChangesWhenLowercased(),
#     "CHANGES_WHEN_TITLECASED": ChangesWhenTitlecased(),
#     "CHANGES_WHEN_UPPERCASED": ChangesWhenUppercased(),
#     "DASH": Dash(),
#     "DEFAULT_IGNORABLE_CODE_POINT": DefaultIgnorableCodePoint(),
#     "DEPRECATED": Deprecated(),
#     "DIACRITIC": Diacritic(),
#     "EMOJI": Emoji(),
#     "EMOJI_COMPONENT": EmojiComponent(),
#     "EMOJI_MODIFIER": EmojiModifier(),
#     "EMOJI_MODIFIER_BASE": EmojiModifierBase(),
#     "EMOJI_PRESENTATION": EmojiPresentation(),
#     "EXTENDED_PICTOGRAPHIC": ExtendedPictographic(),
#     "EXTENDER": Extender(),
#     "GRAPHEME_BASE": GraphemeBase(),
#     "GRAPHEME_EXTEND": GraphemeExtend(),
#     "GRAPHEME_LINK": GraphemeLink(),
#     "HEX_DIGIT": HexDigit(),
#     "HYPHEN": Hyphen(),
#     "IDS_BINARY_OPERATOR": IdsBinaryOperator(),
#     "IDS_TRINARY_OPERATOR": IdsTrinaryOperator(),
#     "ID_CONTINUE": IdContinue(),
#     "ID_START": IdStart(),
#     "IDEOGRAPHIC": Ideographic(),
#     "JOIN_CONTROL": JoinControl(),
#     "LOGICAL_ORDER_EXCEPTION": LogicalOrderException(),
#     "LOWERCASE": Lowercase(),
#     "MATH": Math(),
#     "NONCHARACTER_CODE_POINT": NoncharacterCodePoint(),
#     "OTHER_ALPHABETIC": OtherAlphabetic(),
#     "OTHER_DEFAULT_IGNORABLE_CODE_POINT": OtherDefaultIgnorableCodePoint(),
#     "OTHER_GRAPHEME_EXTEND": OtherGraphemeExtend(),
#     "OTHER_ID_CONTINUE": OtherIdContinue(),
#     "OTHER_ID_START": OtherIdStart(),
#     "OTHER_LOWERCASE": OtherLowercase(),
#     "OTHER_MATH": OtherMath(),
#     "OTHER_UPPERCASE": OtherUppercase(),
#     "PATTERN_SYNTAX": PatternSyntax(),
#     "PATTERN_WHITE_SPACE": PatternWhiteSpace(),
#     "PREPENDED_CONCATENATION_MARK": PrependedConcatenationMark(),
#     "QUOTATION_MARK": QuotationMark(),
#     "RADICAL": Radical(),
#     "REGIONAL_INDICATOR": RegionalIndicator(),
#     "SENTENCE_TERMINAL": SentenceTerminal(),
#     "SOFT_DOTTED": SoftDotted(),
#     "TERMINAL_PUNCTUATION": TerminalPunctuation(),
#     "UNIFIED_IDEOGRAPH": UnifiedIdeograph(),
#     "UPPERCASE": Uppercase(),
#     "VARIATION_SELECTOR": VariationSelector(),
#     "WHITE_SPACE": WhiteSpace(),
#     "XID_CONTINUE": XidContinue(),
#     "XID_START": XidStart(),
# }


# UNICODE_SCRIPT_PROPERTY_RULES = {
#     "ADLAM": Adlam(),
#     "AHOM": Ahom(),
#     "ANATOLIAN_HIEROGLYPHS": AnatolianHieroglyphs(),
#     "ARABIC": Arabic(),
#     "ARMENIAN": Armenian(),
#     "AVESTAN": Avestan(),
#     "BALINESE": Balinese(),
#     "BAMUM": Bamum(),
#     "BASSA_VAH": BassaVah(),
#     "BATAK": Batak(),
#     "BENGALI": Bengali(),
#     "BHAIKSUKI": Bhaiksuki(),
#     "BOPOMOFO": Bopomofo(),
#     "BRAHMI": Brahmi(),
#     "BRAILLE": Braille(),
#     "BUGINESE": Buginese(),
#     "BUHID": Buhid(),
#     "CANADIAN_ABORIGINAL": CanadianAboriginal(),
#     "CARIAN": Carian(),
#     "CAUCASIAN_ALBANIAN": CaucasianAlbanian(),
#     "CHAKMA": Chakma(),
#     "CHAM": Cham(),
#     "CHEROKEE": Cherokee(),
#     "CHORASMIAN": Chorasmian(),
#     "COMMON": Common(),
#     "COPTIC": Coptic(),
#     "CUNEIFORM": Cuneiform(),
#     "CYPRIOT": Cypriot(),
#     "CYPRO_MINOAN": CyproMinoan(),
#     "CYRILLIC": Cyrillic(),
#     "DESERET": Deseret(),
#     "DEVANAGARI": Devanagari(),
#     "DIVES_AKURU": DivesAkuru(),
#     "DOGRA": Dogra(),
#     "DUPLOYAN": Duployan(),
#     "EGYPTIAN_HIEROGLYPHS": EgyptianHieroglyphs(),
#     "ELBASAN": Elbasan(),
#     "ELYMAIC": Elymaic(),
#     "ETHIOPIC": Ethiopic(),
#     "GEORGIAN": Georgian(),
#     "GLAGOLITIC": Glagolitic(),
#     "GOTHIC": Gothic(),
#     "GRANTHA": Grantha(),
#     "GREEK": Greek(),
#     "GUJARATI": Gujarati(),
#     "GUNJALA_GONDI": GunjalaGondi(),
#     "GURMUKHI": Gurmukhi(),
#     "HAN": Han(),
#     "HANGUL": Hangul(),
#     "HANIFI_ROHINGYA": HanifiRohingya(),
#     "HANUNOO": Hanunoo(),
#     "HATRAN": Hatran(),
#     "HEBREW": Hebrew(),
#     "HIRAGANA": Hiragana(),
#     "IMPERIAL_ARAMAIC": ImperialAramaic(),
#     "INHERITED": Inherited(),
#     "INSCRIPTIONAL_PAHLAVI": InscriptionalPahlavi(),
#     "INSCRIPTIONAL_PARTHIAN": InscriptionalParthian(),
#     "JAVANESE": Javanese(),
#     "KAITHI": Kaithi(),
#     "KANNADA": Kannada(),
#     "KATAKANA": Katakana(),
#     "KAWI": Kawi(),
#     "KAYAH_LI": KayahLi(),
#     "KHAROSHTHI": Kharoshthi(),
#     "KHITAN_SMALL_SCRIPT": KhitanSmallScript(),
#     "KHMER": Khmer(),
#     "KHOJKI": Khojki(),
#     "KHUDAWADI": Khudawadi(),
#     "LAO": Lao(),
#     "LATIN": Latin(),
#     "LEPCHA": Lepcha(),
#     "LIMBU": Limbu(),
#     "LINEAR_A": LinearA(),
#     "LINEAR_B": LinearB(),
#     "LISU": Lisu(),
#     "LYCIAN": Lycian(),
#     "LYDIAN": Lydian(),
#     "MAHAJANI": Mahajani(),
#     "MAKASAR": Makasar(),
#     "MALAYALAM": Malayalam(),
#     "MANDAIC": Mandaic(),
#     "MANICHAEAN": Manichaean(),
#     "MARCHEN": Marchen(),
#     "MASARAM_GONDI": MasaramGondi(),
#     "MEDEFAIDRIN": Medefaidrin(),
#     "MEETEI_MAYEK": MeeteiMayek(),
#     "MENDE_KIKAKUI": MendeKikakui(),
#     "MEROITIC_CURSIVE": MeroiticCursive(),
#     "MEROITIC_HIEROGLYPHS": MeroiticHieroglyphs(),
#     "MIAO": Miao(),
#     "MODI": Modi(),
#     "MONGOLIAN": Mongolian(),
#     "MRO": Mro(),
#     "MULTANI": Multani(),
#     "MYANMAR": Myanmar(),
#     "NABATAEAN": Nabataean(),
#     "NAG_MUNDARI": NagMundari(),
#     "NANDINAGARI": Nandinagari(),
#     "NEW_TAI_LUE": NewTaiLue(),
#     "NEWA": Newa(),
#     "NKO": Nko(),
#     "NUSHU": Nushu(),
#     "NYIAKENG_PUACHUE_HMONG": NyiakengPuachueHmong(),
#     "OGHAM": Ogham(),
#     "OL_CHIKI": OlChiki(),
#     "OLD_HUNGARIAN": OldHungarian(),
#     "OLD_ITALIC": OldItalic(),
#     "OLD_NORTH_ARABIAN": OldNorthArabian(),
#     "OLD_PERMIC": OldPermic(),
#     "OLD_PERSIAN": OldPersian(),
#     "OLD_SOGDIAN": OldSogdian(),
#     "OLD_SOUTH_ARABIAN": OldSouthArabian(),
#     "OLD_TURKIC": OldTurkic(),
#     "OLD_UYGHUR": OldUyghur(),
#     "ORIYA": Oriya(),
#     "OSAGE": Osage(),
#     "OSMANYA": Osmanya(),
#     "PAHAWH_HMONG": PauCinHau(),
#     "PALMYRENE": Palmyrene(),
#     "PAU_CIN_HAU": PauCinHau(),
#     "PHAGS_PA": PhagsPa(),
#     "PHOENICIAN": Phoenician(),
#     "PSALTER_PAHLAVI": PsalterPahlavi(),
#     "REJANG": Rejang(),
#     "RUNIC": Runic(),
#     "SAMARITAN": Samaritan(),
#     "SAURASHTRA": Saurashtra(),
#     "SHARADA": Sharada(),
#     "SHAVIAN": Shavian(),
#     "SIDDHAM": Siddham(),
#     "SIGNWRITING": Signwriting(),
#     "SINHALA": Sinhala(),
#     "SOGDIAN": Sogdian(),
#     "SORA_SOMPENG": SoraSompeng(),
#     "SOYOMBO": Soyombo(),
#     "SUNDANESE": Sundanese(),
#     "SYLOTI_NAGRI": SylotiNagri(),
#     "SYRIAC": Syriac(),
#     "TAGALOG": Tagalog(),
#     "TAGBANWA": Tagbanwa(),
#     "TAI_LE": TaiLe(),
#     "TAI_THAM": TaiTham(),
#     "TAI_VIET": TaiViet(),
#     "TAKRI": Takri(),
#     "TAMIL": Tamil(),
#     "TANGSA": Tangsa(),
#     "TANGUT": Tangut(),
#     "TELUGU": Telugu(),
#     "THAANA": Thaana(),
#     "THAI": Thai(),
#     "TIBETAN": Tibetan(),
#     "TIFINAGH": Tifinagh(),
#     "TIRHUTA": Tirhuta(),
#     "TOTO": Toto(),
#     "UGARITIC": Ugaritic(),
#     "VAI": Vai(),
#     "VITHKUQI": Vithkuqi(),
#     "WANCHO": Wancho(),
#     "WARANG_CITI": WarangCiti(),
#     "YEZIDI": Yezidi(),
#     "YI": Yi(),
#     "ZANABAZAR_SQUARE": ZanabazarSquare(),
# }


def make_registry(
    prop_type: str, mapping: dict[str, str]
) -> dict[str, UnicodePropertyRule]:
    """Build registry of Unicode properties.

    Args:
        prop_type: The Unicode property type ("Script", "gc", "Binary").
        mapping: Dict of {UPPERCASE_NAME: Unicode property value}.
    """
    registry = {}
    for key, value in mapping.items():
        if prop_type in ("gc", "Binary"):
            pattern = rf"\p{{{value}}}"
        elif prop_type == "Script":
            pattern = rf"\p{{Script={value}}}"
        else:
            raise ValueError(f"Unknown property type: {prop_type}")
        registry[key] = UnicodePropertyRule(pattern, key)
    return registry


# === Example: General Category registry ===
GENERAL_CATEGORY_MAP = {
    "LETTER": "L",
    "CASED_LETTER": "LC",
    "UPPERCASE_LETTER": "Lu",
    "LOWERCASE_LETTER": "Ll",
    "TITLECASE_LETTER": "Lt",
    "MODIFIER_LETTER": "Lm",
    "OTHER_LETTER": "Lo",
    # ... add MARK, NUMBER, etc.
}

UNICODE_GENERAL_CATEGORY_RULES = make_registry("gc", GENERAL_CATEGORY_MAP)


# === Example: Binary property registry ===
BINARY_PROPERTY_MAP = {
    "ALPHABETIC": "Alphabetic",
    "BIDI_CONTROL": "Bidi_Control",
    "BIDI_MIRRORED": "Bidi_Mirrored",
    "CASE_IGNORABLE": "Case_Ignorable",
    # ... add the rest
}

UNICODE_BINARY_PROPERTY_RULES = make_registry("Binary", BINARY_PROPERTY_MAP)


# === Example: Script registry ===
SCRIPT_PROPERTY_MAP = {
    "CYRILLIC": "Cyrillic",
    "OLD_NORTH_ARABIAN": "Old_North_Arabian",
    "LATIN": "Latin",
    "GREEK": "Greek",
    # ... add the full list
}

UNICODE_SCRIPT_PROPERTY_RULES = make_registry("Script", SCRIPT_PROPERTY_MAP)
