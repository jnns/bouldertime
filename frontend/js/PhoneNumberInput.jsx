import React from "react";

const storageName = "bouldertime:phoneNumber";

class PhoneNumberInput extends React.Component {
  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.state = { phoneNumber: localStorage.getItem(storageName) };
  }
  handleChange(e) {
    const phoneNumber = e.target.value;
    this.setState({ phoneNumber: phoneNumber });
    localStorage.setItem(storageName, phoneNumber);
  }
  render() {
    return (
      <input
        name="phone_no"
        type="text"
        required
        placeholder="+491234567890"
        pattern="\+[1-9]\d{7,14}"
        defaultValue={this.state.phoneNumber}
        onChange={this.handleChange}
      />
    );
  }
}

export default PhoneNumberInput;
