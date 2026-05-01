// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice
#include "wg_interface/msg/detail/zero__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
wg_interface__msg__Zero__init(wg_interface__msg__Zero * msg)
{
  if (!msg) {
    return false;
  }
  // structure_needs_at_least_one_member
  return true;
}

void
wg_interface__msg__Zero__fini(wg_interface__msg__Zero * msg)
{
  if (!msg) {
    return;
  }
  // structure_needs_at_least_one_member
}

bool
wg_interface__msg__Zero__are_equal(const wg_interface__msg__Zero * lhs, const wg_interface__msg__Zero * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // structure_needs_at_least_one_member
  if (lhs->structure_needs_at_least_one_member != rhs->structure_needs_at_least_one_member) {
    return false;
  }
  return true;
}

bool
wg_interface__msg__Zero__copy(
  const wg_interface__msg__Zero * input,
  wg_interface__msg__Zero * output)
{
  if (!input || !output) {
    return false;
  }
  // structure_needs_at_least_one_member
  output->structure_needs_at_least_one_member = input->structure_needs_at_least_one_member;
  return true;
}

wg_interface__msg__Zero *
wg_interface__msg__Zero__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wg_interface__msg__Zero * msg = (wg_interface__msg__Zero *)allocator.allocate(sizeof(wg_interface__msg__Zero), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(wg_interface__msg__Zero));
  bool success = wg_interface__msg__Zero__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
wg_interface__msg__Zero__destroy(wg_interface__msg__Zero * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    wg_interface__msg__Zero__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
wg_interface__msg__Zero__Sequence__init(wg_interface__msg__Zero__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wg_interface__msg__Zero * data = NULL;

  if (size) {
    data = (wg_interface__msg__Zero *)allocator.zero_allocate(size, sizeof(wg_interface__msg__Zero), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = wg_interface__msg__Zero__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        wg_interface__msg__Zero__fini(&data[i - 1]);
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
wg_interface__msg__Zero__Sequence__fini(wg_interface__msg__Zero__Sequence * array)
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
      wg_interface__msg__Zero__fini(&array->data[i]);
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

wg_interface__msg__Zero__Sequence *
wg_interface__msg__Zero__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wg_interface__msg__Zero__Sequence * array = (wg_interface__msg__Zero__Sequence *)allocator.allocate(sizeof(wg_interface__msg__Zero__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = wg_interface__msg__Zero__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
wg_interface__msg__Zero__Sequence__destroy(wg_interface__msg__Zero__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    wg_interface__msg__Zero__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
wg_interface__msg__Zero__Sequence__are_equal(const wg_interface__msg__Zero__Sequence * lhs, const wg_interface__msg__Zero__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!wg_interface__msg__Zero__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
wg_interface__msg__Zero__Sequence__copy(
  const wg_interface__msg__Zero__Sequence * input,
  wg_interface__msg__Zero__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(wg_interface__msg__Zero);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    wg_interface__msg__Zero * data =
      (wg_interface__msg__Zero *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!wg_interface__msg__Zero__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          wg_interface__msg__Zero__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!wg_interface__msg__Zero__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
