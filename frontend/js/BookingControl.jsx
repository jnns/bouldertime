import React from "react";

import Day from "./Day";
import Form from "./Form";

class BookingControl extends React.Component {
  constructor(props) {
    super(props);
    this.state = { startHour: null, endHour: null };
    this.onHourSelect = this.onHourSelect.bind(this);
  }
  onHourSelect(hour) {
    this.setState({ startHour: hour });
  }
  render() {
    return (
      <>
        <Day
          attendance={this.props.attendance}
          bookables={this.props.bookables}
          onHourSelect={this.onHourSelect}
        />
        {this.state.startHour ? (
          <Form
            selectedHour={this.state.startHour}
            startOptions={Object.keys(this.props.bookables)}
            endOptions={this.props.bookables[this.state.startHour]}
            onHourSelect={this.onHourSelect}
          />
        ) : null}
      </>
    );
  }
}

export default BookingControl;
