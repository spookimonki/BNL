// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wg_interface:msg/Zero.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/zero.hpp"


#ifndef WG_INTERFACE__MSG__DETAIL__ZERO__STRUCT_HPP_
#define WG_INTERFACE__MSG__DETAIL__ZERO__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__wg_interface__msg__Zero __attribute__((deprecated))
#else
# define DEPRECATED__wg_interface__msg__Zero __declspec(deprecated)
#endif

namespace wg_interface
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Zero_
{
  using Type = Zero_<ContainerAllocator>;

  explicit Zero_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit Zero_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations

  // pointer types
  using RawPtr =
    wg_interface::msg::Zero_<ContainerAllocator> *;
  using ConstRawPtr =
    const wg_interface::msg::Zero_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wg_interface::msg::Zero_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wg_interface::msg::Zero_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wg_interface::msg::Zero_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wg_interface::msg::Zero_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wg_interface::msg::Zero_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wg_interface::msg::Zero_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wg_interface::msg::Zero_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wg_interface::msg::Zero_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wg_interface__msg__Zero
    std::shared_ptr<wg_interface::msg::Zero_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wg_interface__msg__Zero
    std::shared_ptr<wg_interface::msg::Zero_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Zero_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const Zero_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Zero_

// alias to use template instance with default allocator
using Zero =
  wg_interface::msg::Zero_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace wg_interface

#endif  // WG_INTERFACE__MSG__DETAIL__ZERO__STRUCT_HPP_
