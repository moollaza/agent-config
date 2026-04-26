# Cleanup Implementation

Evaluate and simplify code changes before committing, once the implementation is working.

## When to Use

**Use this command before committing**, after implementation is complete and working:

- Review changes for structural simplification
- Remove excess complexity
- Optimize for readability and maintainability
- Eliminate redundant code and abstractions
- Ensure code is ready for commit

**Timing:** After implementation works, before `git commit`

## Initial Response

When this command is invoked, respond with:

```
I'll review the changes made in this session and simplify them for maintainability and clarity before committing. Let me analyze what was implemented.
```

Then proceed with the cleanup process.

## Cleanup Process

### Step 1: Review Changes

1. **Identify all modified files**:

   ```bash
   git status
   git diff --name-only
   ```

2. **Review each change**:
   - Read all modified files completely
   - Understand what was added/changed
   - Note any patterns or abstractions introduced

### Step 2: Structural Simplification

Evaluate changes for:

- **Unnecessary abstractions** - Remove layers that don't add value
- **Over-engineering** - Simplify complex patterns that aren't needed
- **Speculative design** - Remove code for future features that aren't required
- **Redundant patterns** - Consolidate duplicate logic or structures

### Step 3: Code Quality Improvements

Apply modern coding standards:

- **Language-native constructs** - Use idiomatic patterns for the language
- **Simpler control flow** - Reduce nesting, early returns, clearer logic
- **Direct implementation** - Favor straightforward code over clever abstractions
- **Clear naming** - Ensure names accurately describe purpose

### Step 4: Remove Redundancy

Eliminate:

- **Unused imports/dependencies** - Remove anything not directly used
- **Dead code** - Remove commented-out code, unused functions
- **Temporary code** - Remove debug code, TODOs, placeholder implementations
- **Duplicate logic** - Consolidate repeated patterns

### Step 5: Optimize for Maintainability

Ensure:

- **Every component has clear purpose** - No decorative or speculative code
- **Minimal complexity** - Simple, readable implementation
- **Performance maintained** - Simplification doesn't degrade performance
- **Functionality preserved** - All original behavior still works

### Step 6: Verification

1. **Check for unused code**:

   ```bash
   # Run linters/analyzers for unused imports/variables
   # Language-specific checks
   ```

2. **Verify functionality**:

   - Run tests to ensure nothing broke
   - Verify core functionality still works
   - Check that simplification preserved behavior

3. **Review final diff**:

   ```bash
   git diff
   ```

4. **Prepare for commit**:
   - Ensure all changes are staged or ready to stage
   - Verify cleanup is complete
   - Confirm code is ready for commit

## Guidelines

### What to Simplify

- **Complex abstractions** → Direct implementation
- **Over-engineered patterns** → Simple, clear code
- **Redundant layers** → Flatten where possible
- **Speculative code** → Remove if not needed now
- **Verbose implementations** → Concise, readable code

### What to Keep

- **Functional requirements** - Don't remove needed features
- **Performance optimizations** - Keep if necessary
- **Clear structure** - Maintain logical organization
- **Error handling** - Don't simplify away robustness

### What to Remove

- **Unused imports/dependencies**
- **Commented-out code**
- **Debug/temporary code**
- **Redundant abstractions**
- **Unused functions/variables**
- **Over-complicated patterns**

## Output Format

Present cleanup changes as:

```
## Cleanup Summary

### Files Modified
- `path/to/file.ext` - Simplified [description]

### Simplifications Made
1. [What was simplified and why]
2. [Another simplification]

### Removed
- [What was removed and why]

### Preserved
- [What was kept and why]

### Verification
- [ ] Tests pass
- [ ] Functionality verified
- [ ] No unused code remaining
```

## Notes

- **Use before committing** - This is a pre-commit cleanup step
- **Implementation must be working first** - Don't simplify before functionality is verified
- **Don't degrade performance** - Simplification should maintain or improve performance
- **Preserve functionality** - All original behavior must still work
- **Be thorough** - Review all modified files, not just the most obvious ones
- **Test after changes** - Verify simplification didn't break anything
- **Ask if unclear** - If unsure about removing something, ask the user
