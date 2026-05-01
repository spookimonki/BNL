// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wg_interface:msg/ControlEvent.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wg_interface/msg/control_event.hpp"


#ifndef WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__STRUCT_HPP_
#define WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__wg_interface__msg__ControlEvent __attribute__((deprecated))
#else
# define DEPRECATED__wg_interface__msg__ControlEvent __declspec(deprecated)
#endif

namespace wg_interface
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ControlEvent_
{
  using Type = ControlEvent_<ContainerAllocator>;

  explicit ControlEvent_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->control_type = 0;
      this->right_cycle = 0.0;
      this->right_direction = 0;
      this->left_cycle = 0.0;
      this->left_direction = 0;
      this->combined_cycle = 0.0;
      this->combined_direction = 0;
      this->combined_rotation = 0;
    }
  }

  explicit ControlEvent_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->control_type = 0;
      this->right_cycle = 0.0;
      this->right_direction = 0;
      this->left_cycle = 0.0;
      this->left_direction = 0;
      this->combined_cycle = 0.0;
      this->combined_direction = 0;
      this->combined_rotation = 0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _control_type_type =
    uint8_t;
  _control_type_type control_type;
  using _right_cycle_type =
    double;
  _right_cycle_type right_cycle;
  using _right_direction_type =
    uint8_t;
  _right_direction_type right_direction;
  using _left_cycle_type =
    double;
  _left_cycle_type left_cycle;
  using _left_direction_type =
    uint8_t;
  _left_direction_type left_direction;
  using _combined_cycle_type =
    double;
  _combined_cycle_type combined_cycle;
  using _combined_direction_type =
    uint8_t;
  _combined_direction_type combined_direction;
  using _combined_rotation_type =
    uint8_t;
  _combined_rotation_type combined_rotation;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__control_type(
    const uint8_t & _arg)
  {
    this->control_type = _arg;
    return *this;
  }
  Type & set__right_cycle(
    const double & _arg)
  {
    this->right_cycle = _arg;
    return *this;
  }
  Type & set__right_direction(
    const uint8_t & _arg)
  {
    this->right_direction = _arg;
    return *this;
  }
  Type & set__left_cycle(
    const double & _arg)
  {
    this->left_cycle = _arg;
    return *this;
  }
  Type & set__left_direction(
    const uint8_t & _arg)
  {
    this->left_direction = _arg;
    return *this;
  }
  Type & set__combined_cycle(
    const double & _arg)
  {
    this->combined_cycle = _arg;
    return *this;
  }
  Type & set__combined_direction(
    const uint8_t & _arg)
  {
    this->combined_direction = _arg;
    return *this;
  }
  Type & set__combined_rotation(
    const uint8_t & _arg)
  {
    this->combined_rotation = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    wg_interface::msg::ControlEvent_<ContainerAllocator> *;
  using ConstRawPtr =
    const wg_interface::msg::ControlEvent_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wg_interface::msg::ControlEvent_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wg_interface::msg::ControlEvent_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wg_interface__msg__ControlEvent
    std::shared_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wg_interface__msg__ControlEvent
    std::shared_ptr<wg_interface::msg::ControlEvent_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ControlEvent_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->control_type != other.control_type) {
      return false;
    }
    if (this->right_cycle != other.right_cycle) {
      return false;
    }
    if (this->right_direction != other.right_direction) {
      return false;
    }
    if (this->left_cycle != other.left_cycle) {
      return false;
    }
    if (this->left_direction != other.left_direction) {
      return false;
    }
    if (this->combined_cycle != other.combined_cycle) {
      return false;
    }
    if (this->combined_direction != other.combined_direction) {
      return false;
    }
    if (this->combined_rotation != other.combined_rotation) {
      return false;
    }
    return true;
  }
  bool operator!=(const ControlEvent_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ControlEvent_

// alias to use template instance with default allocator
using ControlEvent =
  wg_interface::msg::ControlEvent_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace wg_interface

#endif  // WG_INTERFACE__MSG__DETAIL__CONTROL_EVENT__STRUCT_HPP_
