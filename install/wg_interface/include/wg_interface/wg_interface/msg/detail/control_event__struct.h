// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wg_interface:msg/ControlEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/control_event.h"


#ifndef WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__STRUCT_H_
#define WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/ControlEvent in the package wg_interface.
typedef struct wg_interface__msg__ControlEvent
{
  std_msgs__msg__Header header;
  /// Hvilken type signal du sender
  uint8_t control_type;
  /// prosent hvor mye av maks frekvens (hel prosent 50% = 50)
  double right_cycle;
  /// tall som representerer retningen på motoren 0, 1
  uint8_t right_direction;
  /// prosent hvor mye av maks frekvens (hel prosent 50% = 50)
  double left_cycle;
  /// tall som representerer retningen på motoren 0, 1
  uint8_t left_direction;
  /// prosent hvor mye av maks frekvens (hel prosent 50% = 50)
  double combined_cycle;
  /// tall som representerer retning 0, 1
  uint8_t combined_direction;
  /// 0 = mot klokka, 1 = med klokka
  uint8_t combined_rotation;
} wg_interface__msg__ControlEvent;

// Struct for a sequence of wg_interface__msg__ControlEvent.
typedef struct wg_interface__msg__ControlEvent__Sequence
{
  wg_interface__msg__ControlEvent * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wg_interface__msg__ControlEvent__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__STRUCT_H_
