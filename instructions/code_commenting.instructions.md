---
name: "coding"
description: "Best practices for writing comments in source code files."
applyTo: "**"
---

# Best Practices when Commenting

Commenting code is a crucial part of the software development process.
Comments enable a reader unfamiliar with the project to quickly understand the **what**, the **why**, and the **how** of the software.
When [writing code](./coding.instructions.md), please follow these instructions to comment the code appropriately.

## How to Comment

The following should have comments attached to them such that an onlooker completely unfamiliar with the code can understand their purpose:

* All functions
* All data structures, enums, and other objects
* All source code files (each file should have a brief header describing the code it contains)
* All global-scope, file-scope, etc., definitions of consts and other values
* All code blocks within a function (a brief, 1-2 sentence comment should describe what each code block is doing).

When necessary, reference other functions or files in your comments by specifying their exact names within backticks (ex: `function_name`).

## How *NOT* to Comment

There are some things that you *must* avoid while writing comments:

* You must have absolutely *zero* mentions of people, other agents, agent-related information that is not relevant to the code, references to code review feedback points, or *any* other metadata that is in your context during the development process (unless explicitly asked to).
    * **Examples of what to avoid:**
        * `// This function now accepts an additional parameter (Code Review - 1.3a)`
        * `// This constant is used below and replaces a previously hard-coded value (P6)`
        * `// - Written by Byteboy`
        * `// This function was changed to do ... as requested by Connor`
* You must have absolutely *zero* references the previous state of the code.
    * You do not need to explain the reasoning or the differences between the current state versus the old state.
    * Code comments must always describe the *exact*, *current* state of the of the code, and *nothing else*.

## Examples

This section shows examples of good commenting practices.
These examples can be applied to any language, despite the language-specific examples given.

### Example 1 - Enums

([Link to file](https://github.com/cwshugg/gurthang/blob/master/src/mutator.c))

```c
// ======================= Mutator Data Structure(s) ======================= //
// This enum is used to define various fuzzing strategies choosable by the
// mutator when fuzzing a given comux file.
typedef enum gurthang_mutate_strategy
{
    STRAT_CHUNK_DATA_HAVOC,     // Random AFL-like fuzzing on chunk data
    STRAT_CHUNK_DATA_EXTRA,     // Additional havoc-like fuzzing
    STRAT_CHUNK_SCHED_BUMP,     // Try modifying a chunk's 'sched' field
    STRAT_CHUNK_SPLIT,          // Split a chunk into two chunks
    STRAT_CHUNK_SPLICE,         // Combine two chunks of the same connection
    STRAT_CHUNK_DICT_SWAP,      // Swap a word in a dictionary for another
    // ----------------------
    STRAT_LENGTH,               // Used to store the number of strategies
    // ----------------------
    STRAT_FIXUP,                // Fix/remake a broken comux input
    STRAT_UNKNOWN               // Used as an 'uninitialized' value
} gurthang_strategy_t;
```

### Example 2 - Structs

([Link to file](https://github.com/cwshugg/gurthang/blob/master/src/preload.c))

```c
// Simple struct that contains an integer, representing a socket file
// descriptor. Used to store a list of currently-active connections to the
// target server (returned by chunk threads).
typedef struct connection_table_entry
{
    int fd;                     // The connection file descriptor
    ctable_status_t status;     // The status of this entry
} ctable_entry_t;
```

### Example 3 - Function Snippet

([Link to file](https://github.com/cwshugg/gurthang/blob/master/src/preload.c))

```c
// Helper routine that sends the comux chunk's data across the socket
// connection to the target server.
// Returns the number of bytes sent to the server.
static size_t PFX(chunk_send_data)(comux_cinfo_t* cinfo, int sockfd)
{
    // Get a pointer to the chunk's data and setup looping variables
    char* dptr = buffer_dptr(&cinfo->data);
    size_t interval_size = cinfo->len > chunk_thread_write_buffsize ?
                           chunk_thread_write_buffsize : cinfo->len;
    ssize_t wcount = 0;
    size_t total_wcount = 0;

    // Repeatedly invoke send() until all bytes from the chunk's data segment
    // have been sent to the target server.
    //
    // We use MSG_NOSIGNAL as a flag to prevent it from generating the SIGPIPE
    // signal if the server closes the connection.
    while ((wcount = send(sockfd, dptr + wcount,
                          MIN(cinfo->len - total_wcount, interval_size),
                          MSG_NOSIGNAL)) > 0)
    { total_wcount += wcount; }
```

### Example 4 - Structs

([Link to file](https://github.com/cwshugg/ragtag/blob/master/src/parser/cursor.rs))

```rust
/// Tracks position through input text for the parser.
///
/// Maintains byte offset, 1-based line, and 1-based column counts
/// incrementally as characters are consumed.
#[derive(Debug)]
pub struct Cursor<'a> {
    /// The full input text.
    input: &'a str,
    /// Current byte offset (0-based).
    pub pos: usize,
    /// Current line number (1-based).
    pub line: usize,
    /// Current column number (1-based).
    pub col: usize,
}
```

### Example 5 - File Header Comment

([Link to file](https://github.com/cwshugg/ragtag/blob/master/src/parser/cursor.rs))

```rust
//! Cursor for tracking position through input text.
//!
//! The `Cursor` is the foundational building block of the hand-rolled parser.
//! It tracks the current byte position, line number, and column number
//! as it advances character-by-character through a `&str` input.
```

### Example 6 - Function

```python
    def run(self):
        """The thread's main function."""
        self.log("Spawned.")

        # loop forever
        while True:
            # Pop from the queue (this will block if the queue is empty).
            action = self.queue.pop()

            # Process the action we received from the queue:
            if action.action == "on":
                self.log("Found queued ON action for ID \"%s\"." % action.lid)
                try:
                    # This is an `on` action; run the `power_on` function with
                    # the action's parameters.
                    self.service.power_on(action.lid,
                                          color=action.color,
                                          brightness=action.brightness)
                except Exception as e:
                    # If running the `on` action fails, log the failure.
                    self.log("Failed to turn device \"%s\" on: %s" % (action.lid, e))
            elif action.action == "off":
                self.log("Found queued OFF action for ID \"%s\"." % action.lid)
                try:
                    # This is an `off` action; run the `power_off` function
                    # with the action's parameters.
                    self.service.power_off(action.lid)
                except Exception as e:
                    # If running the `off` action fails, log the failure.
                    self.log("Failed to turn device \"%s\" off: %s" % (action.lid, e))
            else:
                # This is neither an `on` nor an `off` action. There is no
                # other supported action, so this is unexpected; write to the
                # log.
                self.log("Found unknown action: \"%s\"." % action.action)
```

### Example 7 - Global Dictionary

```python
# ============================ Bang Preprocessor ============================= #
# An extensible bang-command processing system for string values.
#
# Bang commands use the syntax `!keyword content` (e.g. `!file path`).
# New commands can be added at any time by calling `register_bang()`.

# A restricted set of builtins allowed in `!list` bang evaluation.
_LIST_SAFE_BUILTINS = {
    "range": range,
    "int": int,
    "float": float,
    "str": str,
    "len": len,
    "list": list,
    "tuple": tuple,
    "set": set,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "round": round,
    "sorted": sorted,
    "reversed": reversed,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
}
```

