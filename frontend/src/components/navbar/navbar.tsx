import React from "react";
import { Button } from "primereact/button";
import logo from "../../assets/logo-erlangen.png";

const Navbar: React.FC = () => {
  return (
    <nav
      style={{ backgroundColor: "#48c6b1", color: "white", padding: "1rem" }}
    >
      <div style={{ display: "flex", alignItems: "center" }}>
        <img src={logo} width={250}/>
        <ul style={{ listStyle: "none", display: "flex", gap: "1rem" }}>
          <li>
            <Button label="Chatbot" text style={{ color: "white" }} />
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
