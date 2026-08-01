# CKO Knowledge Provenance Statement Foundation — Model Guide

A statement describes one subject. Entities are declared sources, inputs, originals, contributing sources or supporting entities. Actors are declared in closed roles. An optional activity describes an alleged occurrence, while evidence identifies alleged support. None of these references is resolved.

Categories enforce the approved category/activity/entity/actor matrix. Attribution requires an actor; generation, transformation, adaptation, extraction and incorporation require their matching activity. Category and subject determine logical identity. Content changes preserve identity and create the next revision.

Revision 1 is version `1.0.0`; revision `n` is `1.0.(n-1)`. `previous_revision` records succession and remains separate from causal `predecessors`. A supplied set may contain roots, multiple roots, multiple predecessors, partial chains and disconnected components. Detected cycles and conflicting references are rejected.

Qualifier values form a closed JSON tree: null, bool, bounded int, NFC string, canonical array or canonical object. Arrays and objects have distinct private representations. Arrays can be heterogeneous; `[null,true,false,0,-12]` is valid. Float, Decimal, bytes, datetime, tuple ambiguity, sets and arbitrary objects are rejected.

`KnowledgeProvenance` remains legacy Knowledge Object metadata and is never promoted or converted implicitly.
