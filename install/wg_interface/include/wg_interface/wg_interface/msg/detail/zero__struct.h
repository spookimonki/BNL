// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/zero.h"


#ifndef WG_INTERFACE__MSG__DETAIL__ZERO__STRUCT_H_
#define WG_INTERFACE__MSG__DETAIL__ZERO__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/Zero in the package wg_interface.
/**
  * bare en placeholder fil intil videre
 */
typedef struct wg_interface__msg__Zero
{
  uint8_t structure_needs_at_least_one_member;
} wg_interface__msg__Zero;

// Struct for a sequence of wg_interface__msg__Zero.
typedef struct wg_interface__msg__Zero__Sequence
{
  wg_interface__msg__Zero * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wg_interface__msg__Zero__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WG_INTERFACE__MSG__DETAIL__ZERO__STRUCT_H_
