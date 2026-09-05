import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

class ECUCinemaSQL(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ECU Cinema Booking System")
        self.geometry("1000x700")
        self.configure(bg="#2b2b2b")
        
        self.selected_movie = tk.StringVar()
        self.selected_time = tk.StringVar()
        
        # Top Navigation Bar
        self.nav_frame = tk.Frame(self, bg="#1e1e1e", pady=15)
        self.nav_frame.pack(fill="x", side="top")
        tk.Label(self.nav_frame, text="الدفع .4  <-  المأكولات والمشروبات .3  <-  المقاعد .2  <-  الفيلم .1", 
                 font=("Arial", 14, "bold"), bg="#1e1e1e", fg="#f1c40f").pack()

        # Main Container for Pages
        self.container = tk.Frame(self, bg="#2b2b2b")
        self.container.pack(fill="both", expand=True)

        self.conn = self.connect_db()
        self.restart_app()

    def connect_db(self):
        try:
            # NOTE: Server name must match your actual SQL Server instance name.
            # Check it in SSMS -> Object Explorer (top-left), e.g. "localhost\SQLEXPRESS"
            # or "YOUR-PC-NAME\SQLEXPRESS". Using "." only works for a *default*
            # (unnamed) instance, which is not the case here.
            return pyodbc.connect(
                'DRIVER={SQL Server};'
                'SERVER=localhost\\SQLEXPRESS;'
                'DATABASE=CinemaDB_Pro;'
                'Trusted_Connection=yes;'
            )
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return None

    def restart_app(self):
        # Function to reset variables and start a new booking (Restart)
        self.selected_movie.set("")
        self.selected_time.set("")
        self.selected_seats = []
        self.cart_items = {}
        self.seat_total = 0.0
        self.food_total = 0.0
        self.discount = 0.0
        self.show_movie_page()

    def clear(self):
        for w in self.container.winfo_children(): w.destroy()

    # ================= STEP 1: Movie Selection =================
    def show_movie_page(self):
        self.clear()
        tk.Label(self.container, text="🎬 اختر الفيلم المفضل والموعد", font=("Arial", 20, "bold"), bg="#2b2b2b", fg="white").pack(pady=40)
        
        movies = []
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT Title FROM Movies")
            movies = [row[0] for row in cursor.fetchall()]
            
        ttk.Combobox(self.container, textvariable=self.selected_movie, values=movies, font=("Arial", 16), width=45, justify="right", state="readonly").pack(pady=15)
        ttk.Combobox(self.container, textvariable=self.selected_time, values=["10:00 AM", "12:00 PM", "01:00 PM", "03:00 PM", "06:00 PM", "07:30 PM", "09:00 PM", "10:30 PM"], font=("Arial", 16), width=45, justify="right", state="readonly").pack(pady=15)

        tk.Button(self.container, text="استمرار لاختيار المقاعد <-", font=("Arial", 16, "bold"), bg="#e74c3c", fg="white", width=25, command=self.show_seat_page).pack(pady=40)

    # ================= STEP 2: Seat Selection =================
    def show_seat_page(self):
        if not self.selected_movie.get() or not self.selected_time.get():
            messagebox.showwarning("تنبيه", "برجاء اختيار الفيلم والموعد أولاً"); return
        self.clear()
        tk.Label(self.container, text="(IMAX Screen) شاشة العرض", font=("Arial", 16), bg="#2b2b2b", fg="#bdc3c7").pack(pady=20)
        
        grid = tk.Frame(self.container, bg="#2b2b2b")
        grid.pack()

        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT SeatName, SeatType, Price, Status FROM Seats")
            for i, (s_name, s_type, s_price, s_status) in enumerate(cursor.fetchall()):
                bg_color = "#3498db" if s_type == "Standard" else "#f1c40f"
                if s_status == 'Booked': bg_color = "#7f8c8d" 
                
                btn = tk.Button(grid, text=s_name, width=6, height=2, bg=bg_color, fg="black", font=("Arial", 11, "bold"))
                btn.grid(row=i//8, column=i%8, padx=6, pady=6)
                
                # Assign command to ALL buttons, passing the status to handle validation
                btn.config(command=lambda n=s_name, p=s_price, st=s_status, b=btn: self.handle_seat_click(n, p, st, b))

        tk.Button(self.container, text="التالي: قائمة المأكولات <-", font=("Arial", 16, "bold"), bg="#e74c3c", fg="white", command=self.show_food_page).pack(pady=30)

    def handle_seat_click(self, name, price, status, btn):
        # Validate if seat is already booked to prevent duplication
        if status == 'Booked':
            messagebox.showerror("خطأ في الحجز", "عفواً، لا يمكن حجز هذا المقعد لأنه محجوز مسبقاً لعميل آخر!")
        else:
            self.toggle_seat(name, price, btn)

    def toggle_seat(self, name, price, btn):
        if name in self.selected_seats:
            self.selected_seats.remove(name); self.seat_total -= float(price); btn.config(text=name)
        else:
            self.selected_seats.append(name); self.seat_total += float(price); btn.config(text="✔")

    # ================= STEP 3: Food and Drinks =================
    def show_food_page(self):
        self.clear()
        mf = tk.Frame(self.container, bg="#2b2b2b")
        mf.pack(fill="both", expand=True, padx=20, pady=20)
        
        cart_f = tk.Frame(mf, bg="#1e1e1e", width=250, bd=2, relief="groove")
        cart_f.pack(side="left", fill="y", padx=10)
        tk.Label(cart_f, text="🛒 سلة طلباتك", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="#f1c40f").pack(pady=10)
        self.cart_lbl = tk.Label(cart_f, text="", font=("Arial", 13), bg="#1e1e1e", fg="white", justify="right")
        self.cart_lbl.pack(pady=10)

        drinks_f = tk.Frame(mf, bg="#2b2b2b")
        drinks_f.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(drinks_f, text="🥤 المشروبات", font=("Arial", 16, "bold"), bg="#2b2b2b", fg="#34dbeb").pack(pady=10)
        
        food_f = tk.Frame(mf, bg="#2b2b2b")
        food_f.pack(side="right", fill="both", expand=True, padx=10)
        tk.Label(food_f, text="🍿 المأكولات", font=("Arial", 16, "bold"), bg="#2b2b2b", fg="#e67e22").pack(pady=10)

        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT ItemName, Price, Category FROM Menu")
            for name, price, cat in cursor.fetchall():
                parent = food_f if cat == 'Food' else drinks_f
                card = tk.Frame(parent, bg="#34495e", bd=1, relief="ridge", pady=5, padx=10)
                card.pack(fill="x", pady=5, padx=10)
                
                tk.Label(card, text=f"{name} ({price} ج.م)", font=("Arial", 12, "bold"), bg="#34495e", fg="white").pack(side="right")
                tk.Button(card, text="➕ إضافة", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), bd=0, activebackground="#27ae60", command=lambda n=name, p=price: self.add_food(n, p)).pack(side="left")

        tk.Button(self.container, text="الذهاب للدفع <-", font=("Arial", 16, "bold"), bg="#e74c3c", fg="white", width=25, command=self.show_checkout_page).pack(pady=20)

    def add_food(self, name, price):
        self.food_total += float(price)
        self.cart_items[name] = self.cart_items.get(name, 0) + 1
        self.cart_lbl.config(text="\n".join([f"{v}x {k}" for k, v in self.cart_items.items()]) + f"\n\nالإجمالي: {self.food_total} ج.م")

    # ================= STEP 4: Checkout and Promo =================
    def show_checkout_page(self):
        self.clear()
        inv = tk.Frame(self.container, bg="#1e1e1e", bd=2, relief="groove")
        inv.pack(pady=30, padx=150, fill="both")

        tk.Label(inv, text="🧾 مراجعة الفاتورة", font=("Arial", 20, "bold"), bg="#1e1e1e", fg="#f1c40f").pack(pady=15)
        
        tot = self.seat_total + self.food_total
        tk.Label(inv, text=f"تذاكر السينما: {self.seat_total} ج.م\nالمأكولات والمشروبات: {self.food_total} ج.م\nالإجمالي قبل الخصم: {tot} ج.م", font=("Arial", 16), bg="#1e1e1e", fg="white", justify="right").pack(pady=15)

        pf = tk.Frame(inv, bg="#1e1e1e")
        pf.pack(pady=15)
        self.promo_entry = tk.Entry(pf, font=("Arial", 16), justify="center")
        self.promo_entry.pack(side="right", padx=10)
        tk.Button(pf, text="تطبيق كود الخصم", bg="#16a085", fg="white", font=("Arial", 14), command=lambda: self.apply_promo(tot)).pack(side="right")

        self.final_lbl = tk.Label(inv, text=f"الإجمالي النهائي: {tot} ج.م", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="#e74c3c")
        self.final_lbl.pack(pady=20)

        tk.Button(self.container, text="تأكيد الدفع وإصدار التذكرة ✔", font=("Arial", 18, "bold"), bg="#e74c3c", fg="white", command=lambda: self.confirm_booking(tot)).pack(pady=15)

    def apply_promo(self, tot):
        code = self.promo_entry.get()
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DiscountValue FROM PromoCodes WHERE Code=?", (code,))
            res = cursor.fetchone()
            if res:
                self.discount = float(res[0])
                self.final_lbl.config(text=f"الإجمالي النهائي: {tot - self.discount} ج.م")
                messagebox.showinfo("مبروك", f"تم تطبيق الخصم بنجاح!")
            else:
                messagebox.showerror("خطأ", "كود الخصم غير صحيح")

    def confirm_booking(self, tot):
        f_paid = tot - self.discount
        if self.conn:
            cursor = self.conn.cursor()
            try:
                for seat in self.selected_seats:
                    cursor.execute("UPDATE Seats SET Status='Booked' WHERE SeatName=?", (seat,))
                
                cursor.execute("{CALL sp_BookTicket (?, ?, ?, ?)}", (self.selected_movie.get(), self.selected_time.get(), ",".join(self.selected_seats), f_paid))
                self.conn.commit()
                self.show_ticket_page(f_paid)
            except Exception as e:
                messagebox.showerror("SQL Error", str(e))

    # ================= STEP 5: Ticket & Restart =================
    def show_ticket_page(self, f_paid):
        self.clear()
        tf = tk.Frame(self.container, bg="#1e1e1e", bd=2, relief="ridge")
        tf.pack(pady=20, ipadx=50, ipady=20)

        tk.Label(tf, text="🎟 VIP PREMIUM INVOICE & TICKET", font=("Arial", 20, "bold"), bg="#1e1e1e", fg="#f1c40f").pack(pady=15)
        tk.Label(tf, text=f"بيانات العرض:\n{self.selected_movie.get()}\nالموعد: {self.selected_time.get()}", font=("Arial", 16), bg="#1e1e1e", fg="white").pack(pady=10)
        tk.Label(tf, text=f"المقاعد: {','.join(self.selected_seats)}", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="#3498db").pack()
        tk.Label(tf, text="|||| ||||| |||| |||||", font=("Courier", 35), bg="#1e1e1e", fg="white").pack(pady=15)
        tk.Label(tf, text=f"تم الدفع بنجاح: {f_paid} ج.م", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="#2ecc71").pack()

        tk.Button(self.container, text="إنهاء النظام وبدء حجز جديد 🔄", font=("Arial", 16, "bold"), bg="#34495e", fg="white", activebackground="#2c3e50", command=self.restart_app).pack(pady=20)

if __name__ == "__main__":
    app = ECUCinemaSQL()
    app.mainloop()