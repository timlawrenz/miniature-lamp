# Prompt Strategy for Tiled Upscaling

## TL;DR

**Using the full complex original generation prompt for tiled upscaling is generally NOT recommended.**

**Why?** Each tile only shows part of the image, but the prompt describes the whole scene. FLUX will try to add missing elements from the prompt, causing hallucinations and artifacts.

**Current default:** `"high quality, detailed, sharp"` - A safe, generic prompt that works well.

---

## The Problem

### Example Scenario

**Original prompt:**
```
"A majestic dragon with golden scales breathing fire over a medieval castle, 
surrounded by mountains in the background, knights in the foreground, 
wearing detailed armor with family crests, sunset lighting, cinematic"
```

**What happens when upscaling with tiles:**

| Tile Location | Actual Content | Prompt Says | Problem |
|---------------|----------------|-------------|---------|
| Top-left | Sky | dragon, castle, knights | Tries to add elements |
| Center | Dragon scales | castle, mountains, knights | Confusing guidance |
| Bottom-right | Grass | dragons, castles, knights | Hallucinations |

### Problems This Causes

1. **Hallucination**: FLUX tries to add prompt elements not in that tile
2. **Inconsistency**: Each tile interprets the full prompt differently
3. **Loss of Original**: Strong prompts override the actual content
4. **Seam Issues**: Adjacent tiles generate conflicting interpretations

## Prompt Strategies

### Strategy 1: Generic Quality Prompt ✅ (Current Default)

**Prompt:** `"high quality, detailed, sharp"`

**Pros:**
- Safe - no hallucinations
- Consistent across all tiles
- Preserves original content
- Fast

**Cons:**
- No semantic guidance
- Doesn't use original style intent

**Best for:** Conservative upscaling, photos, general use

---

### Strategy 2: Style-Only Prompt

**Extract style terms from original:**
```
Original: "dragon, castle, sunset lighting, cinematic, detailed"
Extract:  "sunset lighting, cinematic, detailed"
```

**Pros:**
- Preserves lighting/mood
- Maintains style
- No object hallucinations

**Cons:**
- Requires prompt parsing
- Complex to implement

**Best for:** Style-consistent upscaling

---

### Strategy 3: No Prompt (Maximum Preservation)

**Prompt:** `""` (empty)

Relies purely on:
- Input image (img2img strength)
- DINO conditioning (if enabled)

**Pros:**
- Zero text hallucination
- Maximum preservation
- Fastest

**Cons:**
- No quality guidance
- May be bland

**Best for:** Archival/forensic work

---

### Strategy 4: Strength-Dependent (Adaptive)

```python
if strength < 0.2:
    prompt = ""  # Conservative
elif strength < 0.4:
    prompt = "high quality, detailed"
else:
    prompt = user_full_prompt  # Creative mode
```

**Pros:**
- Adapts to user intent
- Balances safety and creativity

**Cons:**
- May surprise users
- Still risky at high strength

**Best for:** Advanced users

---

### Strategy 5: Full Original Prompt ⚠️

**Use with caution!**

**When it might work:**
- Very low strength (< 0.15)
- Simple prompts without specific objects
- Single dominant subject (portrait)

**When it fails:**
- Complex scenes with multiple subjects
- Specific object placement descriptions
- Strength > 0.2

## Recommendations by Use Case

### Photo Enhancement
```python
prompt = "high quality, sharp, detailed"
strength = 0.1-0.2
dino_enabled = True
```

### Artistic Upscale
```python
prompt = "cinematic lighting, detailed, [artistic style]"
strength = 0.2-0.3
dino_enabled = True
dino_strength = 0.6
```

### Maximum Preservation
```python
prompt = ""
strength = 0.05-0.1
dino_enabled = True
dino_strength = 0.7
```

### Creative Enhancement
```python
prompt = "high quality, [style keywords only]"
strength = 0.3-0.4
dino_enabled = True
dino_strength = 0.5
```

## Prompt Guidelines for Users

### ❌ Don't Use

Complex prompts with specific objects/composition:
- "dragon breathing fire over castle with knights"
- "woman in red dress standing under tree on the left"  
- "three cats playing with ball in garden"

These will cause tiles to hallucinate missing elements.

### ✅ Do Use

Quality and style descriptors:
- "high quality, detailed, sharp"
- "cinematic lighting, professional photography"
- "oil painting style, detailed brushwork"
- "soft lighting, detailed textures"

Or simply:
- "" (empty for maximum preservation)

### 💡 Rule of Thumb

**If your prompt describes WHERE things are or WHAT objects exist → Don't use it for tiled upscaling**

**If your prompt describes HOW it looks (style/quality) → Safe to use**

## Interaction with Strength Parameter

The prompt's influence changes with `strength`:

| Strength | Prompt Influence | Recommendation |
|----------|------------------|----------------|
| 0.05-0.1 | Minimal | Any prompt works, even complex |
| 0.1-0.2  | Low | Generic prompts best |
| 0.2-0.3  | Moderate | Style-only prompts |
| 0.3-0.4  | High | Empty or very simple |
| 0.4+     | Very High | Avoid (may lose original) |

**Key insight:** Lower strength = more preservation, less prompt influence

## DINO's Role

DINO conditioning provides **semantic guidance** about what's actually in each tile:

### With Strong DINO (0.5-0.7):
- Can use simpler prompts safely
- DINO prevents hallucinations
- Prompt just guides quality/style

### With Weak DINO (0.0-0.3):
- Prompt has more influence
- Need more careful prompt selection
- Higher hallucination risk

### DINO + Prompt Together:
- **DINO**: "This tile contains dragon scales"
- **Prompt**: "Make it sharp and detailed"
- **Result**: Sharp detailed dragon scales ✓

Without DINO:
- **Prompt**: "dragon, castle, knights, detailed"
- **Tile content**: Just scales
- **Result**: Confusing mix, possible hallucinations ✗

## What Other Upscalers Do

### Ultimate SD Upscale
- Uses full original prompt
- Adds "upscaled, detailed"
- Problem: Hallucinations common
- Solution: Seam-fix modes to blend artifacts

### Tiled Diffusion
- Supports prompt per tile
- User can specify regions
- Complex but powerful

### Commercial Tools (Topaz, Gigapixel)
- No text prompts at all
- Pure learning-based enhancement
- No hallucination issues

## Implementation Suggestions

### Option A: Keep Current + Document ✅

Current implementation is good:
- Generic default prompt
- User can override
- Just needs better documentation

**Action:** Update README with prompt guidelines

### Option B: Add Prompt Mode Parameter

```python
"prompt_mode": (
    ["generic", "style_only", "none", "custom"],
    {"default": "generic"}
)
```

Automatically select appropriate prompt.

### Option C: Automatic Based on Strength

```python
if strength < 0.15:
    effective_prompt = prompt  # User's full prompt OK
elif strength < 0.3:
    effective_prompt = "high quality, detailed, sharp"
else:
    effective_prompt = ""  # Maximum preservation
```

## Testing Results

Test with different scenarios:

1. **Portrait** (simple subject)
   - Generic prompt: ✓ Works well
   - Full prompt: ✓ Often works (single subject)

2. **Complex scene** (multiple subjects)
   - Generic prompt: ✓ Safe, good results
   - Full prompt: ✗ Hallucinations likely

3. **Variable strength**
   - Low (0.1): Full prompt tolerable
   - Medium (0.2): Generic prompt best
   - High (0.4): Empty prompt safest

## Current Implementation

```python
def upscale(self, ..., prompt="high quality, detailed, sharp"):
    # Uses generic default
    # User can override via parameter
```

**Status:**
- ✓ Safe default chosen
- ✓ User can customize
- ✗ No documentation about strategy
- ✗ No automatic optimization

## Recommended Documentation for Node README

Add this section:

```markdown
### Prompt Parameter

**Default**: `"high quality, detailed, sharp"`

The prompt guides FLUX during upscaling. Because upscaling processes 
tiles independently, use **style/quality terms only**, not object 
descriptions.

**Guidelines:**
- ✅ Good: "high quality, detailed, sharp, cinematic lighting"
- ✅ Good: "professional photography, detailed textures"
- ❌ Bad: "dragon breathing fire over castle" (causes hallucinations)
- ❌ Bad: "woman in red dress on left side" (tiles don't match)

**Tip**: For maximum preservation of the original, use empty prompt `""`

**Strength interaction:**
- strength < 0.2: Prompt has less effect (safer to use complex prompts)
- strength > 0.3: Prompt has strong effect (use simple prompts only)
```

## Conclusion

**Answer to your question:** Using the full complex original prompt is **generally not useful** and often **harmful** for tiled upscaling because:

1. ❌ Each tile doesn't contain all prompt elements  
2. ❌ FLUX tries to add missing elements (hallucination)
3. ❌ Creates inconsistency between tiles
4. ❌ Can override the actual image content

**Better approach:**
- ✅ Generic quality prompts (current default)
- ✅ Style/lighting keywords only
- ✅ Empty prompt for maximum preservation
- ⚠️ Full prompt only at very low strength (<0.15)

**The current implementation's generic default prompt is actually a smart choice!**

It provides quality guidance without causing hallucinations. Users can still override it, but should be warned about the risks of complex prompts.
