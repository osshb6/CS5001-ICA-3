import streamlit as st
from calculator import add, subtract, multiply, divide

def main():
    st.title("Simple Calculator")

    num1 = st.number_input("Enter first number")
    num2 = st.number_input("Enter second number")
    operation = st.selectbox("Select operation", ["Add", "Subtract", "Multiply", "Divide"])

    if st.button("Calculate"):
        try:
            if operation == "Add":
                result = add(num1, num2)
            elif operation == "Subtract":
                result = subtract(num1, num2)
            elif operation == "Multiply":
                result = multiply(num1, num2)
            elif operation == "Divide":
                result = divide(num1, num2)
            st.write(f"Result: {result}")
        except ValueError as e:
            st.error(e)

if __name__ == "__main__":
    main()
