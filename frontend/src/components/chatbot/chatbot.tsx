import React from "react";
import { InputTextarea } from "primereact/inputtextarea";
import Messages from "./messages";

const Chatbot: React.FC = () => {
  let value = "";
  const setValue = (v: string) => {
    value = v;
  };

  return (
    <>
      <div
        style={{
          height: "100%",
        }}
      >
        <div
          style={{
            height: "100%",
          }}
        >
          <Messages />
        </div>
        <form
          style={{
            display: "flex",
            backgroundColor: "#ffffff",
            borderColor: "#dfe7ef",
            border: "solid 1px 1px",
            padding: "1rem",
            borderRadius: "0.5rem",
          }}
        >
          <InputTextarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            rows={1}
            cols={30}
          />
        </form>
      </div>
    </>
  );
};

export default Chatbot;
