import React from "react";

import Hour from "./Hour";

class Day extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hour: null };
    this.onClick = this.onClick.bind(this);
  }
  onClick(hour) {
    this.setState({ hour: hour });
    this.props.onHourSelect(hour);
  }
  render() {
    return (
      <div className="day">
        {Object.keys(this.props.attendance).map((hour) => (
          <Hour
            key={hour}
            hour={hour}
            attendance={this.props.attendance[hour]}
            onClick={this.onClick}
            selected={this.state.hour == hour}
          />
        ))}
      </div>
    );
  }
}

export default Day;
