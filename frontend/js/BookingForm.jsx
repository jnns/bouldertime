import React from "react";
import DjangoCSRFToken from "django-react-csrftoken";
import PhoneNumberInput from "./PhoneNumberInput";

class BookingForm extends React.Component {
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
          defaultValue={this.props.endOptions[0]}
          disabled={Boolean(!endOptions.length)}
        >
          {endOptions}
        </select>
        <p>
          <label>
            Your cell phone number: <PhoneNumberInput />
          </label>
        </p>
        <p>
          <input type="submit" value="Request booking code" />
        </p>
      </form>
    );
  }
}

export default BookingForm;
