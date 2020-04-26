import React from "react";
import DjangoCSRFToken from "django-react-csrftoken";
import PhoneNumberInput from "./PhoneNumberInput";

class Form extends React.Component {
  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.state = {
      phone_no: localStorage.getItem("bouldertime:phone_no") || "",
    };
  }
  handleChange(e) {
    this.props.onHourSelect(e.target.value);
  }
  render() {
    const startOptions = this.props.startOptions.map((hour) => (
      <option key={hour} value={hour}>
        {hour}:00
      </option>
    ));
    const endOptions = this.props.endOptions.map((hour) => (
      <option key={hour} value={hour}>
        {hour}:00
      </option>
    ));
    return (
      <form method="post">
        <DjangoCSRFToken />
        <select
          name="start"
          value={this.props.selectedHour}
          onChange={this.handleChange}
        >
          {startOptions}
        </select>
        &nbsp;&mdash;&nbsp;
        <select
          name="end"
          value={this.props.endOptions[0]}
          onChange={this.handleChange}
          disabled={Boolean(!endOptions.length)}
        >
          {endOptions}
        </select>
        <label>
          Your cell phone number: <PhoneNumberInput />
        </label>
        <input type="submit" value="Request booking code" />
      </form>
    );
  }
}

export default Form;
