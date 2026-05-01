// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from wg_interface:msg/ControlEvent.idl
// generated code does not contain a copyright notice
#include "wg_interface/msg/detail/control_event__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
wg_interface__msg__ControlEvent__init(wg_interface__msg__ControlEvent * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    wg_interface__msg__ControlEvent__fini(msg);
    return false;
  }
  // control_type
  // right_cycle
  // right_direction
  // left_cycle
  // left_direction
  // combined_cycle
  // combined_direction
  // combined_rotation
  return true;
}

void
wg_interface__msg__ControlEvent__fini(wg_interface__msg__ControlEvent * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // control_type
  // right_cycle
  // right_direction
  // left_cycle
  // left_direction
  // combined_cycle
  // combined_direction
  // combined_rotation
}

bool
wg_interface__msg__ControlEvent__are_equal(const wg_interface__msg__ControlEvent * lhs, const wg_interface__msg__ControlEvent * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // control_type
  if (lhs->control_type != rhs->control_type) {
    return false;
  }
  // right_cycle
  if (lhs->right_cycle != rhs->right_cycle) {
    return false;
  }
  // right_direction
  if (lhs->right_direction != rhs->right_direction) {
    return false;
  }
  // left_cycle
  if (lhs->left_cycle != rhs->left_cycle) {
    return false;
  }
  // left_direction
  if (lhs->left_direction != rhs->left_direction) {
    return false;
  }
  // combined_cycle
  if (lhs->combined_cycle != rhs->combined_cycle) {
    return false;
  }
  // combined_direction
  if (lhs->combined_direction != rhs->combined_direction) {
    return false;
  }
  // combined_rotation
  if (lhs->combined_rotation != rhs->combined_rotation) {
    return false;
  }
  return true;
}

bool
wg_interface__msg__ControlEvent__copy(
  const wg_interface__msg__ControlEvent * input,
  wg_interface__msg__ControlEvent * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // control_type
  output->control_type = input->control_type;
  // right_cycle
  output->right_cycle = input->right_cycle;
  // right_direction
  output->right_direction = input->right_direction;
  // left_cycle
  output->left_cycle = input->left_cycle;
  // left_direction
  output->left_direction = input->left_direction;
  // combined_cycle
  output->combined_cycle = input->combined_cycle;
  // combined_direction
  output->combined_direction = input->combined_direction;
  // combined_rotation
  output->combined_rotation = input->combined_rotation;
  return true;
}

wg_interface__msg__ControlEvent *
wg_interface__msg__ControlEvent__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wg_interface__msg__ControlEvent * msg = (wg_interface__msg__ControlEvent *)allocator.allocate(sizeof(wg_interface__msg__ControlEvent), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(wg_interface__msg__ControlEvent));
  bool success = wg_interface__msg__ControlEvent__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
wg_interface__msg__ControlEvent__destroy(wg_interface__msg__ControlEvent * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    wg_interface__msg__ControlEvent__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
wg_interface__msg__ControlEvent__Sequence__init(wg_interface__msg__ControlEvent__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wg_interface__msg__ControlEvent * data = NULL;

  if (size) {
    data = (wg_interface__msg__ControlEvent *)allocator.zero_allocate(size, sizeof(wg_interface__msg__ControlEvent), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = wg_interface__msg__ControlEvent__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        wg_interface__msg__ControlEvent__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
wg_interface__msg__ControlEvent__Sequence__fini(wg_interface__msg__ControlEvent__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      wg_interface__msg__ControlEvent__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

wg_interface__msg__ControlEvent__Sequence *
wg_interface__msg__ControlEvent__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wg_interface__msg__ControlEvent__Sequence * array = (wg_interface__msg__ControlEvent__Sequence *)allocator.allocate(sizeof(wg_interface__msg__ControlEvent__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = wg_interface__msg__ControlEvent__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
wg_interface__msg__ControlEvent__Sequence__destroy(wg_interface__msg__ControlEvent__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    wg_interface__msg__ControlEvent__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
wg_interface__msg__ControlEvent__Sequence__are_equal(const wg_interface__msg__ControlEvent__Sequence * lhs, const wg_interface__msg__ControlEvent__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!wg_interface__msg__ControlEvent__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
wg_interface__msg__ControlEvent__Sequence__copy(
  const wg_interface__msg__ControlEvent__Sequence * input,
  wg_interface__msg__ControlEvent__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(wg_interface__msg__ControlEvent);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    wg_interface__msg__ControlEvent * data =
      (wg_interface__msg__ControlEvent *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!wg_interface__msg__ControlEvent__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          wg_interface__msg__ControlEvent__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!wg_interface__msg__ControlEvent__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
