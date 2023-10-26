#HƯỚNG DẪN SETUP. Chắc chắn rồi đầu tiên bạn phải chạy trên phần mềm chạy được python (trừ python online)
#nếu chạy sinh lỗi, hãy vào cmd và nhập 'pip install tk'/'pip install winsound' rồi nhấn Enter
#không được nữa hỏi chủ kiki
#cảm ơn vì đã chơi!

import tkinter as tk
from tkinter import messagebox
import random
import winsound
import time

class SlotMachineGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Trò chơi máy đánh bạc (@Qu4nh)")

        # Lấy kích thước màn hình
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Tính toán vị trí x và y để căn giữa cửa sổ
        x_position = int((screen_width - 500) / 2)
        y_position = int((screen_height - 550) / 2)

        self.root.geometry(f"500x550+{x_position}+{y_position}")  # Thiết lập kích thước và vị trí cửa sổ

        self.money = 1000
        self.bet_amount = 50
        self.luck = 0  # Tỉ lệ may mắn của người chơi bắt đầu từ 0%
        self.lucky_price = 2  # Giá ban đầu cho vật phẩm Lucky
        self.red_spin_price = 500  # Giá vật phẩm Red Spin
        self.red_spin_chance = 30  # Tăng tỉ lệ trúng cho lần quay tiếp theo, giới hạn tối đa là 100
        self.more_coin_price = 5  # Giá ban đầu cho vật phẩm More Coin
        self.more_coin_multiplier = 1  # Hệ số nhân cho vật phẩm More Coin

        self.invalid_message_id = None

        self.icons = {
            "💎": {"name": "Diamond", "probability": 5, "multiplier": 5},
            "🔔": {"name": "Bell", "probability": 8, "multiplier": 3.5},
            "🍒": {"name": "Cherry", "probability": 12, "multiplier": 3},
            "⭐": {"name": "Star", "probability": 20, "multiplier": 2},
            "❤️": {"name": "Heart", "probability": 25, "multiplier": 1.75},
            "🍀": {"name": "Clover", "probability": 30, "multiplier": 1.5},
            
        }

        temp=[5,8,12,30,50,70]

        self.label_money = tk.Label(root, text=f"Tiền: {self.money}", fg="green")
        self.label_money.pack()

        self.label_luck = tk.Label(root, text=f"May mắn: {self.luck}%", fg="darkorange")
        self.label_luck.pack()

        self.label_bet = tk.Label(root, text="Cược: ")
        self.label_bet.pack()

        self.bet_frame = tk.Frame(root)
        self.bet_frame.pack()

        self.made_by_label = tk.Label(root, text="Made by QuAnh", font=("Helvetica", 10), fg="gray")
        self.made_by_label.place(anchor="sw", relx=0, rely=1, x=10, y=-10)

        self.bet_entry = tk.Entry(self.bet_frame, validate="key")
        self.bet_entry.config(validatecommand=(self.bet_entry.register(self.validate_bet), "%P"))
        self.bet_entry.bind("<Return>", self.update_bet_entry)
        self.bet_entry.pack(side="left")

        self.enter_label = tk.Label(self.bet_frame, text="(Nhấn Enter)", font=("Helvetica", 10), fg="gray", anchor="w")
        self.enter_label.pack(side="left")

        self.bet_slider = tk.Scale(root, from_=1, to=5000, orient="horizontal", length=400, command=self.update_bet_slider)
        self.bet_slider.set(self.bet_amount)
        self.bet_slider.pack()

        self.spin_button = tk.Button(root, text="Quay", command=self.spin)
        self.spin_button.pack()

        self.result_label = tk.Label(root, text="", font=("Helvetica", 20))
        self.result_label.pack()

        self.win_label = tk.Label(root, text="", font=("Helvetica", 16))
        self.win_label.pack()

        self.icon_info_label = tk.Label(root, text="", font=("Helvetica", 12), anchor="nw", justify="left")
        self.update_icon_info()
        self.icon_info_label.pack(side="left", padx=10, pady=10)

        self.shop_button = tk.Button(root, text="Cửa hàng", command=self.open_shop)
        self.shop_button.pack()

        self.shop_window = None  # Lưu cửa sổ cửa hàng để theo dõi

        self.add_money_button = tk.Button(root, text="Thêm Tiền", command=self.add_money)
        self.add_money_button.place(x=10, y=10)

        self.add_winner_button()

    def add_winner_button(self):
        winner_button = tk.Button(self.root, text="Trở thành người chiến thắng", command=self.become_winner)
        winner_button.pack(side="bottom", fill="both", padx=10, pady=10, expand=True)

    def become_winner(self):
        target_money = 50000
        if self.money >= target_money:
            self.label_money.config(text=f"Tiền: {self.money} ")
            self.show_winner_message()
        else:
            remaining_money = target_money - self.money
            self.show_purchase_message("Không đủ tiền", f"Bạn cần thêm {remaining_money} tiền nữa để trở thành người chiến thắng.")

    def show_winner_message(self):
        num_windows = 30  # Số lượng cửa sổ kín màn hình muốn hiển thị
        total_windows = num_windows

        def play_error_sound():
            # Phát âm thanh lỗi của Windows
            winsound.Beep(200, 10)  # Tần số 500Hz, thời gian 500ms

        def show_winner_message_window():
            nonlocal num_windows
            winner_message = tk.Toplevel(self.root)
            winner_message.title("Congratulations!")

            # Set the geometry of the winner message window and center it on the screen
            winner_message_width = 800
            winner_message_height = 400
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = random.randint(0, screen_width - winner_message_width)
            y = random.randint(0, screen_height - winner_message_height)
            winner_message.geometry(f"{winner_message_width}x{winner_message_height}+{x}+{y}")

            # Create a label to display the message
            message_label = tk.Label(winner_message, text="Chúc mừng bạn đã trở thành người chiến thắng!", font=("Helvetica", 30), bg="yellow", wraplength=winner_message_width - 20, justify="center")
            message_label.pack(fill="both", expand=True)

            play_error_sound()  # Phát âm thanh lỗi khi hiển thị cửa sổ

            num_windows -= 1
            if num_windows > 0:
                self.root.after(1, show_winner_message_window)  # Tăng tốc độ hiển thị cửa sổ
            else:
                self.root.after(3000, lambda: [win.destroy() for win in self.root.winfo_children() if win.winfo_class() == "Toplevel"])
                num_windows = total_windows
                time.sleep(5)
                import webbrowser
                webbrowser.open("https://www.youtube.com/watch?v=lvOG5Ycvha4")

        show_winner_message_window()
        

    
    def add_money(self):
        self.money += int(self.more_coin_multiplier)
        self.label_money.config(text=f"Tiền: {self.money}")
        self.update_shop_label()  # Cập nhật giá của vật phẩm "More Coin"

    def open_shop(self):
        if not self.shop_window:
            self.shop_window = tk.Toplevel(self.root)
            self.shop_window.title("Shop")

            # Set the shop window position to the right of the main window
            x_position = self.root.winfo_x() + self.root.winfo_width()
            y_position = self.root.winfo_y()
            self.shop_window.geometry(f"+{x_position}+{y_position}")

            # Add widgets to the shop window
            shop_label = tk.Label(self.shop_window, text="Chào mừng bạn đến với Cửa hàng!")
            shop_label.pack()

            lucky_button = tk.Button(self.shop_window, text=f"Lucky (+2% may mắn) - Giá: {self.lucky_price} xu",
                                 command=self.buy_lucky)
            lucky_button.pack()

            red_spin_button = tk.Button(self.shop_window, text=f"Red Spin (+{self.red_spin_chance}% tỉ lệ trúng) - Giá: {self.red_spin_price} xu",
                                    command=self.buy_red_spin)
            red_spin_button.pack()

            more_coin_button = tk.Button(self.shop_window, text=f"More Coin (+{self.more_coin_multiplier:.2f} xu mỗi lần) - Giá: {self.more_coin_price} xu",
                                     command=self.buy_more_coin)
            more_coin_button.pack()

            special_item_button = tk.Button(self.shop_window, text="Vật phẩm đặc biệt - Giá: 100000 xu",
                                        command=self.open_special_item)
            special_item_button.pack()

            self.more_coin_button = more_coin_button  # Save the button reference for updating the price later

            self.shop_window.protocol("WM_DELETE_WINDOW", self.close_shop)

    def close_shop(self):
        if self.shop_window:
            self.shop_window.destroy()
            self.shop_window = None

    def buy_lucky(self):
        if self.money >= self.lucky_price:
            self.money -= self.lucky_price
            self.luck += 1
            self.update_luck_in_icons()  # Cập nhật tỉ lệ xuất hiện của biểu tượng dựa trên số lucky mới
            self.lucky_price = int(self.lucky_price * 1.5)  # Tăng giá cho lần mua tiếp theo
            self.update_shop_label()
            self.label_money.config(text=f"Money: {self.money}")
            self.update_luck_label()  # Cập nhật số lucky trong cửa sổ chính
            self.update_icon_info()
            self.show_purchase_message("Mua thành công", "Bạn đã mua Lucky! Tỉ lệ thắng đã cao hơn.")
        else:
            self.show_purchase_message("Không Đủ Tiền", "Bạn không có đủ tiền để mua Lucky.")
    def update_luck_label(self):
        self.label_luck.config(text=f"Lucky: {self.luck}%")
    
    def buy_red_spin(self):
        if self.money >= self.red_spin_price:
            self.money -= self.red_spin_price
            self.update_red_spin_chance_in_icons()  # Cập nhật tỉ lệ Red Spin trong biểu tượng
            self.red_spin_price *= 3  # Tăng giá cho lần mua tiếp theo
            self.update_shop_label()
            self.label_money.config(text=f"Tiền: {self.money}")
            self.spin_button.config(text="Red Spin", bg="red", font=("Helvetica", 14, "bold"), command=self.red_spin)
            self.show_purchase_message("Mua Thành Công", f"Bạn đã mua Red Spin! Lần quay tiếp theo của bạn có tỉ lệ trúng cao hơn {self.red_spin_chance}%.")
        else:
            self.show_purchase_message("Không Đủ Tiền", "Bạn không có đủ tiền để mua Red Spin.")

    def buy_more_coin(self):
        if self.money >= self.more_coin_price:
            self.money -= self.more_coin_price
            self.more_coin_multiplier *= 1.25
            self.more_coin_price = int(self.more_coin_price * 1.74)  # Tăng giá cho lần mua tiếp theo
            self.update_shop_label()
            self.label_money.config(text=f"Tiền: {self.money}")
            self.show_purchase_message("Mua Thành Công", "Bạn đã mua More Coin! Số lượng xu nhận từ 'Thêm Tiền' đã được tăng.")
        else:
            self.show_purchase_message("Không Đủ Tiền", "Bạn không có đủ tiền để mua More Coin.")
    
    def update_luck_in_icons(self):
        for icon in self.icons:
            # Tính tỉ lệ biểu tượng mới dựa trên tỉ lệ ban đầu và lucky của người chơi
            probability = self.icons[icon]["probability"] + 1
            probability = min(probability, 100)
            # Cập nhật lại tỉ lệ biểu tượng trong dictionary
            self.icons[icon]["probability"] = probability

    def update_red_spin_chance_in_icons(self):
        for icon in self.icons:
            # Tính tỉ lệ biểu tượng mới dựa trên tỉ lệ ban đầu và red_spin_chance
            probability = self.icons[icon]["probability"] + self.red_spin_chance
            # Giới hạn tỉ lệ biểu tượng tối đa là 100%
            probability = min(probability, 100)
            # Cập nhật lại tỉ lệ biểu tượng trong dictionary
            self.icons[icon]["probability"] = probability

    def show_purchase_message(self, title, message):
        message_box = tk.Toplevel(self.root)
        message_box.title(title)

        # Thiết lập kích thước cửa sổ để vừa vặn nội dung và đặt vào giữa màn hình
        message_label = tk.Label(message_box, text=message)
        message_label.pack(padx=20, pady=10)

        message_box.update_idletasks()  # Cập nhật cửa sổ để lấy kích thước thực tế sau khi đặt label
        window_width = message_box.winfo_width()
        window_height = message_box.winfo_height()

        screen_width = message_box.winfo_screenwidth()
        screen_height = message_box.winfo_screenheight()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        message_box.geometry(f"+{x}+{y}")

        message_box.after(5000, message_box.destroy)  # Tắt cửa sổ thông báo sau 3 giây

    def buy_special_item(self):
        if self.money >= 100000:
            self.money -= 100000
            self.label_money.config(text=f"Tiền: {self.money}")
            self.show_purchase_message("Mua Thành Công", "Bạn đã mua thành công Vật phẩm đặc biệt!")
        else:
            self.show_purchase_message("Không đủ tiền", "Bạn không có đủ tiền để mua Vật phẩm đặc biệt.")

    def open_special_item(self):
        import webbrowser
        webbrowser.open("https://www.youtube.com/watch?v=x2sB0QhzrlE")

    def red_spin(self):
        self.spin()
        self.spin_button.config(text="Quay", bg="SystemButtonFace", font=("Helvetica", 12), command=self.spin)

    def update_shop_label(self):
        lucky_button = self.shop_window.winfo_children()[1]  # Lấy nút trong cửa sổ cửa hàng
        lucky_button.config(text=f"Lucky (+1% may mắn) - Giá: {self.lucky_price} xu")

        red_spin_button = self.shop_window.winfo_children()[2]  # Lấy nút trong cửa sổ cửa hàng
        red_spin_button.config(text=f"Red Spin (+{self.red_spin_chance}% tỉ lệ trúng) - Giá: {self.red_spin_price} xu")

        more_coin_button = self.shop_window.winfo_children()[3]  # Lấy nút trong cửa sổ cửa hàng
        more_coin_button.config(text=f"More Coin (+{self.more_coin_multiplier:.2f} xu mỗi lần) - Giá: {self.more_coin_price} xu")

    def increase_luck_by_30_percent(self):
        if self.red_spin_chance < 30:
            self.red_spin_chance = 30
            for icon in self.icons:
                self.icons[icon]["probability"] += 30

        self.update_icon_info()

    def validate_bet(self, new_value):
        if new_value.isdigit():
            bet_amount = int(new_value)
            if 1 <= bet_amount <= 5000:
                self.bet_amount = bet_amount
                self.enter_label.config(text="(Nhấn Enter)", fg="gray")
                if self.invalid_message_id:
                    self.root.after_cancel(self.invalid_message_id)
            else:
                self.enter_label.config(text="Không hợp lệ", fg="red")
                self.invalid_message_id = self.root.after(1000, self.clear_invalid_message)
        self.bet_entry.delete(0, "end")
        self.bet_entry.insert(0, str(self.bet_amount))
        self.bet_slider.set(self.bet_amount)
        return True

    def clear_invalid_message(self):
        self.enter_label.config(text="(Nhấn Enter)", fg="gray")
        self.invalid_message_id = None

    def update_bet_slider(self, bet_amount):
        self.bet_amount = int(bet_amount)
        self.bet_entry.delete(0, "end")
        self.bet_entry.insert(0, str(self.bet_amount))

    def update_bet_entry(self, event):
        new_value = self.bet_entry.get()
        if new_value.isdigit():
            bet_amount = int(new_value)
            if 1 <= bet_amount <= 5000:
                self.bet_amount = bet_amount
        self.bet_slider.set(self.bet_amount)
        self.bet_entry.delete(0, "end")
        self.bet_entry.insert(0, str(self.bet_amount))

    def validate_bet_amount(self):
        if self.bet_amount > self.money:
            self.show_invalid_bet_message()
            return False
        return True

    def show_invalid_bet_message(self):
        messagebox.showinfo("Cược Không Hợp Lệ", "Bạn không có đủ tiền để đặt cược này. Hãy nhập một số tiền cược hợp lệ.")
        self.spin_button.config(state="normal")
    
    def update_icon_info(self):
        info_text = f"Xác suất Biểu tượng (May mắn: +{self.luck}%):\n"
        for icon, data in self.icons.items():
            # Tính tỉ lệ biểu tượng dựa trên tỉ lệ ban đầu và lucky của người chơi
            probability = data["probability"]
            # Giới hạn tỉ lệ biểu tượng tối đa là 100%
            probability = min(probability, 100)
            info_text += f"{data['name']} ({icon}): {probability}% cơ hội, x{data['multiplier']} phần thưởng\n"
        self.icon_info_label.config(text=info_text)
    
    def spin(self):
        if not self.validate_bet_amount():
            return

        self.money -= self.bet_amount
        self.label_money.config(text=f"Tiền: {self.money}")
        
        # Ẩn nút quay trong lúc hoạt hình quay
        self.spin_button.config(state="disabled")

        # Xóa nhãn chiến thắng trước khi bắt đầu quay
        self.win_label.config(text="")

        self.animate_spin()

    def animate_spin(self, spins=5, delay=150):
        if spins > 0:
            icons = [self.get_random_icon() for _ in range(3)]
            self.result_label.config(text=" ".join(icons))
            self.root.after(delay, self.animate_spin, spins-1, delay)
        else:
            self.show_result()

    def get_random_icon(self):
        rand = random.randint(1, 100)
        total = 0
        for icon, data in self.icons.items():
            total += data["probability"] + self.luck
            if rand <= total:
                return icon

    def show_result(self):
        icons = self.result_label.cget("text").split()
        if len(set(icons)) == 1:  # Tất cả biểu tượng giống nhau
            icon = icons[0]
            self.money += int(self.bet_amount * self.icons[icon]["multiplier"])
            self.win_label.config(text=f"Xin chúc mừng! Bạn đã thắng {int(self.bet_amount * self.icons[icon]['multiplier'])} xu với {self.icons[icon]['name']}!", fg="blue")
            self.label_money.config(text=f"Tiền: {self.money}", fg="green")
        else:
            self.win_label.config(text="Thử lại!", fg="red")

        # Hiện lại nút quay sau khi hiển thị kết quả
        self.spin_button.config(state="normal")

        if self.money <= 0:
            self.game_over()

    def game_over(self):
        self.spin_button.config(state="disabled")
        messagebox.showinfo("Hết Tiền", "Bạn đã hết tiền! Kết thúc trò chơi. Restart để chơi lại")

if __name__ == "__main__":
    root = tk.Tk()
    game = SlotMachineGame(root)
    root.mainloop()