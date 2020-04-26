import React from "react";

class Hour extends React.Component {
  constructor(props) {
    super(props);
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(e) {
    this.props.onClick(this.props.hour);
  }

  render() {
    const available = this.props.attendance < 100;
    return (
      <div
        onClick={this.handleClick}
        data-hour={this.props.hour}
        className={
          "day__hour " + (this.props.selected ? "day__hour--selected" : "")
        }
      >
        <div
          className={
            "hour__attendance " +
            (available
              ? "hour__attendance--available"
              : "hour__attendance--not-available")
          }
          style={{ height: this.props.attendance + "%" }}
        ></div>
      </div>
    );
  }
}

export default Hour;
