import tkinter as tk
 
     try:
        # Update the result display
        force_label.config(state=tk.NORMAL)  # Enable the result box to change the value
        force_label.delete(1.0, tk.END)  # Clear the previous result
        force_label.insert(tk.END, f"{score_force:.1f}")  # Insert the computed result
        force_label.config(state=tk.DISABLED)  # Disable interaction with the result box
    except ValueError:
        # Update the result display
        force_label.config(state=tk.NORMAL)  # Enable the result box to change the value
        force_label.delete(1.0, tk.END)  # Clear the previous result
        force_label.insert(tk.END, "")  # Insert the computed result
        force_label.config(state=tk.DISABLED)  # Disable interaction with the result box

  
    try:  
        # Update the result display
        endu_label.config(state=tk.NORMAL)  # Enable the result box to change the value
        endu_label.delete(1.0, tk.END)  # Clear the previous result
        endu_label.insert(tk.END, f"{score_endu:.1f}")  # Insert the computed result
        endu_label.config(state=tk.DISABLED)  # Disable interaction with the result box
    except ValueError:
        # Update the result display
        endu_label.config(state=tk.NORMAL)  # Enable the result box to change the value
        endu_label.delete(1.0, tk.END)  # Clear the previous result
        endu_label.insert(tk.END, "")  # Insert the computed result
        endu_label.config(state=tk.DISABLED)  # Disable interaction with the result box


    try:
        # Update the result display
        result_label.config(state=tk.NORMAL)  # Enable the result box to change the value
        result_label.delete(1.0, tk.END)  # Clear the previous result
        result_label.insert(tk.END, f"{result:.1f}")  # Insert the computed result
        result_label.config(state=tk.DISABLED)  # Disable interaction with the result box
    except ValueError:
        # Handle invalid inputs (non-numeric or empty fields)
        result_label.config(state=tk.NORMAL)
        result_label.delete(1.0, tk.END)
        result_label.insert(tk.END, "")
        result_label.config(state=tk.DISABLED)
