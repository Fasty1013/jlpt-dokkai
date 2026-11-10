"""Deterministic server-side shuffling of answer options + opaque option tokens (Step 11d).

Anti-Cheat / stability rules
- seed = HMAC(SHUFFLE_SECRET, user_id | text_id | attempt_epoch); `attempt_epoch` is the number of attempts the
  user has already completed for this text, so the order is random per new attempt but identical on page reload,
  backend restart and in the review of that attempt. Nothing is stored.
- The client never sees database option ids: `id` of an option is a 48-bit token derived from the same HMAC
  (fits a JS safe integer, so the `selected_option_id: int` API contract is unchanged). Tokens carry no order
  information and cannot be mapped to the correct answer.
- `option_number` of a shuffled question is the *displayed* position (1..n).
- Questions whose options depend on their order are never shuffled (see `is_order_dependent`).
"""
import hashlib
import hmac
import re
from typing import Any, Dict, List, Optional

from app.core.config import SHUFFLE_SECRET

_TOKEN_BYTES = 6  # 48 bits < 2**53 (JS Number.MAX_SAFE_INTEGER)

# Options that point at other options or at "all/none of the above".
_CROSS_REFERENCE = re.compile(
    r"(選択肢"
    r"|[1-4１-４①-④]\s*(?:と|、|・|か|および|及び)\s*[1-4１-４①-④]"
    r"|[1-4１-４①-④]\s*のどちら"
    r"|^\s*(?:上の|以上の)?\s*(?:すべて|全部|全て|どれ(?:も)?|いずれ(?:も)?|両方|どちら(?:も)?)\s*(?:が|も|は)?\s*(?:正しい|間違い|違う|誤り|当てはまる|同じ|ない|あてはまる)"
    r"|^\s*(?:上の|以上の)(?:すべて|全部|全て|どれ)"
    r"|^\s*(?:A|B|ア|イ)\s*と\s*(?:A|B|ア|イ)\s*(?:両方|の両方)?\s*$)"
)
_DIGITS = re.compile(r"\d+")


def _hmac_int(message: str, nbytes: int = _TOKEN_BYTES) -> int:
    digest = hmac.new(SHUFFLE_SECRET.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return int.from_bytes(digest[:nbytes], "big")


def is_order_dependent(option_texts: List[str]) -> bool:
    """True when the options must keep their original order (white list for shuffling)."""
    if any(_CROSS_REFERENCE.search(t or "") for t in option_texts):
        return True
    # Numeric / date / time options that are sorted (ascending or descending): keep the natural order.
    firsts = []
    for t in option_texts:
        found = _DIGITS.findall(t or "")
        if not found:
            return False
        firsts.append(int(found[0]))
    if len(set(firsts)) > 1 and (firsts == sorted(firsts) or firsts == sorted(firsts, reverse=True)):
        return True
    return False


def option_token(user_id: str, text_id: int, epoch: int, option_id: int) -> int:
    token = _hmac_int(f"tok|{user_id}|{text_id}|{epoch}|{option_id}")
    return token or 1


def present_options(user_id: str, text_id: int, epoch: int, question) -> List[Dict[str, Any]]:
    """Options of a question as the user sees them: [{opt, number, token}], in display order."""
    options = sorted(question.options, key=lambda o: o.option_number)
    if not is_order_dependent([o.option_text for o in options]):
        options = sorted(
            options,
            key=lambda o: (_hmac_int(f"ord|{user_id}|{text_id}|{epoch}|{question.id}|{o.id}", 8), o.id),
        )
    return [
        {"opt": o, "number": i + 1, "token": option_token(user_id, text_id, epoch, o.id)}
        for i, o in enumerate(options)
    ]


def resolve_selected(user_id: str, text_id: int, epoch: int, question, selected: Optional[int],
                     allow_legacy_ids: bool = False) -> Optional[int]:
    """Map a token sent by the client back to the real option id (None if it matches nothing).

    `allow_legacy_ids` also accepts raw option ids; used only to render the review of attempts
    that were stored before option tokens existed.
    """
    if selected is None:
        return None
    for o in question.options:
        if option_token(user_id, text_id, epoch, o.id) == selected:
            return o.id
    if allow_legacy_ids and any(o.id == selected for o in question.options):
        return selected
    return None
