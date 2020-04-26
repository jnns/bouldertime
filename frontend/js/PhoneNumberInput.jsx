import React from "react";

const storage_name = "bouldertime:phone_no";

class PhoneNumberInput extends React.Component {
  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.state = { phone_no: localStorage.getItem(storage_name) };
  }
  handleChange(e) {
    console.log(e.target.value);
    const phone_no = e.target.value;
    this.setState({ phone_no: phone_no });
    localStorage.setItem(storage_name, phone_no);
  }
  render() {
    return (
      <input
        name="phone_no"
        type="text"
        inputMode="numeric"
        pattern="[+/0-9]*"
        defaultValue={this.state.phone_no}
        onChange={this.handleChange}
      />
    );
  }
}

export default PhoneNumberInput;
