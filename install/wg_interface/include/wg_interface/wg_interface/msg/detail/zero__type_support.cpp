// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "wg_interface/msg/detail/zero__functions.h"
#include "wg_interface/msg/detail/zero__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace wg_interface
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void Zero_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) wg_interface::msg::Zero(_init);
}

void Zero_fini_function(void * message_memory)
{
  auto typed_message = static_cast<wg_interface::msg::Zero *>(message_memory);
  typed_message->~Zero();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Zero_message_member_array[1] = {
  {
    "structure_needs_at_least_one_member",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wg_interface::msg::Zero, structure_needs_at_least_one_member),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Zero_message_members = {
  "wg_interface::msg",  // message namespace
  "Zero",  // message name
  1,  // number of fields
  sizeof(wg_interface::msg::Zero),
  false,  // has_any_key_member_
  Zero_message_member_array,  // message members
  Zero_init_function,  // function to initialize message memory (memory has to be allocated)
  Zero_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Zero_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Zero_message_members,
  get_message_typesupport_handle_function,
  &wg_interface__msg__Zero__get_type_hash,
  &wg_interface__msg__Zero__get_type_description,
  &wg_interface__msg__Zero__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace wg_interface


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<wg_interface::msg::Zero>()
{
  return &::wg_interface::msg::rosidl_typesupport_introspection_cpp::Zero_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, wg_interface, msg, Zero)() {
  return &::wg_interface::msg::rosidl_typesupport_introspection_cpp::Zero_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
