// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice

#include "wg_interface/msg/detail/zero__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_wg_interface
const rosidl_type_hash_t *
wg_interface__msg__Zero__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xa3, 0x63, 0xf9, 0x47, 0x44, 0x9e, 0x21, 0x2c,
      0x56, 0x59, 0x4c, 0xb4, 0x6c, 0x25, 0x40, 0x80,
      0xdb, 0x1c, 0xe0, 0x07, 0xbe, 0x66, 0x4d, 0x34,
      0x65, 0x6e, 0x1c, 0xe0, 0xec, 0xd7, 0xe1, 0xcc,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char wg_interface__msg__Zero__TYPE_NAME[] = "wg_interface/msg/Zero";

// Define type names, field names, and default values
static char wg_interface__msg__Zero__FIELD_NAME__structure_needs_at_least_one_member[] = "structure_needs_at_least_one_member";

static rosidl_runtime_c__type_description__Field wg_interface__msg__Zero__FIELDS[] = {
  {
    {wg_interface__msg__Zero__FIELD_NAME__structure_needs_at_least_one_member, 35, 35},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
wg_interface__msg__Zero__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {wg_interface__msg__Zero__TYPE_NAME, 21, 21},
      {wg_interface__msg__Zero__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# bare en placeholder fil intil videre";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
wg_interface__msg__Zero__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {wg_interface__msg__Zero__TYPE_NAME, 21, 21},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 39, 39},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
wg_interface__msg__Zero__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *wg_interface__msg__Zero__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
