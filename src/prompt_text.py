"""
OCEL / OCPM extraction prompts.

Vocabulary used throughout (do not mix synonyms across prompts):
- "object type"  - class of artifact/actor
- "attribute"    - metadata field of one object type
- "event type"   - verb-based action class
- "E-O relation" - link between an event type and an object type
- "O-O relation" - link between two object types

All prompts assume the JSON output schema is injected separately by the
caller. If you call these prompts, make sure the SAME schema string is
appended to every system message, otherwise prompt-quality comparisons
are confounded by schema differences.
"""

# ---------------------------------------------------------------------------
# Shared rules
# ---------------------------------------------------------------------------

general_restrictions = """
# Output constraints
- Extract ONLY what is explicitly stated in the input. Do not assume,
  extrapolate, or add background knowledge. When in doubt, omit.
- Use canonical names: singular, Title Case, no articles
  ("Document", not "the documents"). Use identical spelling for the
  same concept everywhere it appears.
- Every name in a relation MUST appear verbatim in the corresponding
  object_types or event_types list.
- Each entity appears at most once in its list (object_types,
  attributes, event_types, eo_relations, oo_relations).
- Object-to-object relations reference only names from object_types.
- Object-to-event relations reference only names from object_types and
  event_types.
- Return ONLY a JSON object matching the schema provided by the caller.
  No prose, no markdown, no code fences.
"""

# Shared OCEL vocabulary block reused by several prompts.
ocel_definition_claude = """## OCPM concepts

- **Object type** - a class of physical or logical artifacts that
  participate in events. Examples: "Document", "Application", "User".
  NOT object types: descriptive properties, statuses, or section
  headings of the source document.

- **Attribute** - a descriptive property or metadata field of one
  object type. Disambiguation rule: if X only ever appears as metadata
  of Y and never as an independent actor or artifact in an event, X is
  an attribute of Y, not its own object type. Example: "Role" is an
  attribute of User.

- **Event type** - a short verb-based phrase describing a
  process-relevant action, typically verb + object ("Approve Document",
  "Submit Application"). NOT event types: states ("Document Approved"),
  bare nouns ("Approval"), or passive descriptions without a clear
  actor or action.

- **E-O relation** - which object types are affected or referenced by
  an event type. "Create Document" relates to Document (created) and
  User (performer).

- **O-O relation** - a logical or structural link between two object
  types, possibly of the same type (e.g., Document linked to another
  Document, or Document assigned to OrganizationalUnit). NOT O-O
  relations: temporal ordering or mere narrative co-mention without a
  structural link.
"""

ocel_definition_std = """
# Events
An event describes a specific execution of an activity and is the basic unit of an event log. It is associates with a timestamp, the objects it was performed on/with and values for activity attributes.

# Objects
Every object is a uniquely identifiable instance of an object type, for example "order-123". Its has values for the attribute defined for the object type which can differ for different points in time.

# Relationships
Every event is associated with at least one object through an event-to-object relationship. But two objects can be related without sharing an event through an object-to-object relationship.

# Object Types
Every object belongs to a specific object type. Object types refer to a set of attributes that can be different for different objects or even at different points in time for the same object.

```mermaid
erDiagram
  EVENT_TYPE ||--o{ EVENT_ATTRIBUTE : "has attrib."
  EVENT_TYPE ||--o{ EVENT : "has type"
  EVENT_ATTRIBUTE ||--o{ EVENT_ATTRIBUTE_VALUE : "has name"
  EVENT ||--o{ EVENT_ATTRIBUTE_VALUE : "for event"
  EVENT }o--o{ OBJECT : "has objects (qualifier)"
  EVENT }o--|| TIME : "has timestamp"
  OBJECT_TYPE ||--o{ OBJECT_ATTRIBUTE : "has attrib."
  OBJECT_TYPE ||--o{ OBJECT : "has type"
  OBJECT_ATTRIBUTE ||--o{ OBJECT_ATTRIBUTE_VALUE : "has name"
  OBJECT ||--o{ OBJECT_ATTRIBUTE_VALUE : "for object"
  OBJECT }o--o{ OBJECT : "related from-to (qualifier)"
  OBJECT_ATTRIBUTE_VALUE }o--|| TIME : "has timestamp"
```
"""


# ---------------------------------------------------------------------------
# 1. Naive baseline
# ---------------------------------------------------------------------------

naive_system = (
    """You are an expert in object-centric process mining (OCPM).
Your goal is to extract process-relevant entities (object types and
event types) along with their attributes and relations from a text
document, so the underlying process can be modeled.
Extract only from the given input text; do not assume or extrapolate.
"""
    + general_restrictions
)

naive_query = (
    """Extract object types, attributes, event types, and their relations
from the input text.

1. **Object type** - a class of physical or logical artifacts involved
   in one or more events. Examples: "Document", "Application", "User".

2. **Attribute** - a descriptive property or metadata field that
   characterizes an object type but does not stand alone as one.
   Examples: "Version Number" of a Document, "Role" of a User.

3. **Event type** - a short verb-based phrase describing a
   process-relevant action, typically verb + object
   ("Approve Document", "Submit Application").

4. **E-O relation** - which object types are affected or referenced by
   which event types. "Create Document" relates to Document (created)
   and User (performer).

5. **O-O relation** - a logical or structural link between two object
   types, possibly of the same type (e.g., a Document linked to another
   Document, or a Document assigned to an OrganizationalUnit).
"""
    + general_restrictions
)


# ---------------------------------------------------------------------------
# 2. Naive with negative examples
# ---------------------------------------------------------------------------

improved_naive_system = (
    """You are an expert in object-centric process mining (OCPM).
You extract process-relevant entities from a source document so the
underlying process can be modeled.
"""
    + general_restrictions
)

improved_naive_query = (
    """## What to extract

"""
   + ocel_definition_claude
   + "\n"
   + general_restrictions
)
improved_naive_query_ocel = (
    """## What to extract

"""
   + ocel_definition_std
   + "\n"
   + general_restrictions
)


# ---------------------------------------------------------------------------
# 3. Cascade - step 1 (objects + attributes only)
# ---------------------------------------------------------------------------

improved_naive_cascading_step_1_system = (
    ocel_definition_claude
    + """
## Your task (Step 1 of 2)

Extract ONLY object types and attributes. Do not extract event types
or relations yet - those come in step 2.
"""
    + general_restrictions
)

improved_naive_cascading_step_1_system_ocel = (
    ocel_definition_std
    + """
## Your task (Step 1 of 2)

Extract ONLY object types and attributes. Do not extract event types
or relations yet - those come in step 2.
"""
    + general_restrictions
)

improved_naive_cascading_step_1_query = "Extract object types and their attributes from the document."


# ---------------------------------------------------------------------------
# 4. Cascade - step 2 (events + relations, given step 1's output)
# ---------------------------------------------------------------------------

improved_naive_cascading_step_2_system = (
    ocel_definition_claude
    + """
## Your task (Step 2 of 2)

Object types and their attributes have already been identified in
step 1 and will be provided to you as a literal list under the heading
"Known Object Types". Your job is to extract event types, E-O
relations, and O-O relations from the same document.

Constraints specific to this step:
- Every object type in eo_relations and oo_relations MUST appear
  verbatim in the Known Object Types list.
- Every event in eo_relations MUST appear in event_types.
- If the document clearly implies an object type that is missing from
  the Known Object Types list, do NOT invent it inline. Instead, add
  its name to the `missing_object_types` field of the output. The
  caller will reconcile and may re-run step 1.
"""
    + general_restrictions
)

improved_naive_cascading_step_2_system_ocel = (
    ocel_definition_std
    + """
## Your task (Step 2 of 2)

Object types and their attributes have already been identified in
step 1 and will be provided to you as a literal list under the heading
"Known Object Types". Your job is to extract event types, E-O
relations, and O-O relations from the same document.

Constraints specific to this step:
- Every object type in eo_relations and oo_relations MUST appear
  verbatim in the Known Object Types list.
- Every event in eo_relations MUST appear in event_types.
- If the document clearly implies an object type that is missing from
  the Known Object Types list, do NOT invent it inline. Instead, add
  its name to the `missing_object_types` field of the output. The
  caller will reconcile and may re-run step 1.
"""
    + general_restrictions
)

improved_naive_cascading_step_2_query = (
    "Extract event types, E-O relations, and O-O relations per the schema. "
    "If a needed object type is not in the Known Object Types list, add it "
    "to `missing_object_types` rather than inventing it."
)



# ---------------------------------------------------------------------------
# 5. Algorithmic 2 (state-change framing, canonical naming)
# ---------------------------------------------------------------------------

algorithmic_system = (
    """You are an expert at reading processes from text and modeling
them as OCEL entities.

# Rules
- Use short canonical names for entities. Prefer the document's own
  terminology when it is already concise and unambiguous; only
  paraphrase when the document's wording is verbose or inconsistent.
- Each entity exists at most once across the output, even if the
  document mentions it many times.
- Only extract entities involved in the core process described.
- If a new candidate matches an existing entity semantically, merge
  them under the existing name rather than adding a variant.
"""
    + general_restrictions
)

algorithmic_query = (
    ocel_definition_claude
    + """

## Procedure

1. Identify actions in the document that change the state of an
   entity. Each such action is a candidate event type.
2. Identify the entities involved in those actions. These are
   candidate object types.
3. For each event type, record an E-O relation to every object type
   that is the actor, the target, or otherwise directly referenced.
4. For each pair of object types that are structurally linked
   (assignment, ownership, containment, reference), record an O-O
   relation.
5. Every object type and event type listed must appear in at least one
   relation. If it does not, reconsider whether it belongs in the
   output.

Use short, consistent names for object types, event types, attributes,
and relations.
"""
)

algorithmic_query_ocel = (
    ocel_definition_std
    + """

## Procedure

1. Identify actions in the document that change the state of an
   entity. Each such action is a candidate event type.
2. Identify the entities involved in those actions. These are
   candidate object types.
3. For each event type, record an E-O relation to every object type
   that is the actor, the target, or otherwise directly referenced.
4. For each pair of object types that are structurally linked
   (assignment, ownership, containment, reference), record an O-O
   relation.
5. Every object type and event type listed must appear in at least one
   relation. If it does not, reconsider whether it belongs in the
   output.

Use short, consistent names for object types, event types, attributes,
and relations.
"""
)


# ---------------------------------------------------------------------------
# 6. Algorithmic 3 (regulatory documents, structured pass)
# ---------------------------------------------------------------------------

improved_algorithmic_system = (
    """You are an expert at reading regulatory and process
documentation and modeling the described processes as OCEL entities
(object types, attributes, event types, E-O relations, O-O relations).

Keep entities semantically well separated by their role in the
process: an actor is different from an artifact it produces, and a
state is different from the action that produced it.
"""
    + general_restrictions
)

improved_algorithmic_query = (
    ocel_definition_claude
    + """

## Procedure

Read the document end to end, then perform four passes over what you
have read:

1. **Process pass.** Identify each distinct process or sub-process
   described, and for each one note the actors involved, the actions
   they perform, the artifacts they act on, and any conditions or
   attributes mentioned.

2. **Entity pass.** From the process notes, derive:
   - object types (actors and artifacts that participate in actions),
   - attributes (metadata of one object type, no independent role),
   - event types (the actions themselves).
   Merge synonyms under a single canonical name.

3. **Relation pass.** Derive E-O relations (each event type with the
   object types it touches) and O-O relations (each pair of object
   types with a structural link). If an item already appears as an
   attribute of an object type AND as a participant in a relation,
   remove it from the attributes list and keep it as an object type.

4. **Consistency pass.** Confirm that every name in a relation also
   appears in object_types or event_types, that no entity is
   duplicated, and that every object type and event type appears in
   at least one relation. Drop anything that fails this check.

Return only the final JSON object.
"""
)

improved_algorithmic_query_ocel = (
    ocel_definition_std
    + """

## Procedure

Read the document end to end, then perform four passes over what you
have read:

1. **Process pass.** Identify each distinct process or sub-process
   described, and for each one note the actors involved, the actions
   they perform, the artifacts they act on, and any conditions or
   attributes mentioned.

2. **Entity pass.** From the process notes, derive:
   - object types (actors and artifacts that participate in actions),
   - attributes (metadata of one object type, no independent role),
   - event types (the actions themselves).
   Merge synonyms under a single canonical name.

3. **Relation pass.** Derive E-O relations (each event type with the
   object types it touches) and O-O relations (each pair of object
   types with a structural link). If an item already appears as an
   attribute of an object type AND as a participant in a relation,
   remove it from the attributes list and keep it as an object type.

4. **Consistency pass.** Confirm that every name in a relation also
   appears in object_types or event_types, that no entity is
   duplicated, and that every object type and event type appears in
   at least one relation. Drop anything that fails this check.

Return only the final JSON object.
"""
)