# Tag Cleanup Guide

## What Happened?

You're seeing extra tags that were accidentally created. This happened because:

1. **During automated testing** - Test runs created tags with names like "AutoTag", "AutoCreatedTag1", etc.
2. **User input confusion** - When entering tags, some inputs like "y", "n", "True", "False" were interpreted as tag names instead of yes/no responses
3. **No validation** - The previous version didn't prevent single-character tags or reserved words

## Tags You're Seeing

Based on your list, these are accidental tags:
- ❌ `y`, `n` - Single characters (likely from yes/no confusion)
- ❌ `True`, `False` - Reserved words (from question type selections)
- ❌ `AutoTag`, `AutoCreatedTag1`, `AutoCreatedTag2` - Test data
- ❌ `Programming`, `TestTag` - Possibly from test runs
- ✅ `Geography` - Your legitimate tag!

## What I Fixed

✅ **Added validation** to prevent future accidental tags:
- Tags must be at least 2 characters long
- Reserved words like "y", "n", "true", "false", "cancel", etc. are blocked
- Better error messages when tag creation fails

## How to Clean Up

### Option 1: Delete Tags Through the Menu (Recommended)

1. Go to **Main Menu** → **3. Manage Tags**
2. Select **4. Delete Tag**
3. Choose the tags you want to delete
4. Only delete tags that have **0 questions** (unused tags)

**To check which tags are unused:**
1. Go to **Main Menu** → **3. Manage Tags**
2. Select **1. View All Tags (Hierarchical)**
3. Look for tags with **Questions: 0**

### Option 2: Keep Test Tags if They're Useful

If any of these tags are actually useful (like "Programming"), you can:
- Keep them and use them for future questions
- Rename them to something more appropriate

### Tags Safe to Delete

These are definitely safe to delete (unused test/accidental tags):
- `y`, `n` - Single characters, likely mistakes
- `True`, `False` - Reserved words, likely mistakes  
- `AutoTag`, `AutoCreatedTag1`, `AutoCreatedTag2` - Clearly test data
- Any tag with **0 questions**

### Tags to Keep

- `Geography` - Your legitimate tag
- Any tag that has questions assigned to it

## Prevention Going Forward

The new validation will prevent:
- ✅ Single character tags (like "y", "n")
- ✅ Reserved words (like "true", "false", "cancel")
- ✅ Better error messages when tag creation fails

You can still type these words during question creation - they just won't be accepted as tag names.

## Need Help?

If you're unsure which tags to delete:
1. View all tags: **Main Menu** → **3. Manage Tags** → **1. View All Tags**
2. Check the "Questions" count for each tag
3. Tags with 0 questions are safe to delete (unless you plan to use them)

