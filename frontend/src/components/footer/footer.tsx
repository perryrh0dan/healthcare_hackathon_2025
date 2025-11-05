import React from "react";
import { Button } from "primereact/button";

const Footer: React.FC = () => {
  return (
    <footer
      style={{
        backgroundColor: "#f3f5f7",
        color: "black",
        padding: "1rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <p>&copy; 2025 Healthcare Hackathon. All rights reserved.</p>
      <ul style={{ listStyle: "none", display: "flex", gap: "1rem" }}>
        <li>
          <Button label="Contact Us" severity="secondary" text />
          <Button label="Terms of use" severity="secondary" text />
        </li>
      </ul>
    </footer>
  );
};

export default Footer;

