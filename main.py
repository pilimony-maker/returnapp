import os
import cv2
from datetime import datetime
import pandas as pd
from PIL import Image as PILImage

# Kivy 核心組件
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.popup import Popup

# 全域初始化 OpenCV 條碼辨識器
barcode_detector = cv2.BarcodeDetector()


class ReturnQCApp(App):
    def build(self):
        self.title = "退貨極速清點"
        
        # 記憶體資料庫與主檔
        self.records = []
        self.history_batches = ["20261231", "20261015"]
        self.product_master = {
            "4710001001": "經典紅茶 300ml",
            "4710001002": "無糖綠茶 500ml",
            "4710001003": "全脂鮮乳 936ml"
        }

        # 相機狀態控制
        self.capture = None
        self.is_camera_running = False

        # 主版面配置 (垂直)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=6)

        # 1. 頂部補光提示按鈕
        torch_btn = Button(
            text="💡 昏暗提醒：請往下滑開選單啟動手機手電筒",
            size_hint_y=None, height=40,
            background_color=(0.95, 0.61, 0.07, 1)
        )
        torch_btn.bind(on_press=lambda instance: self.show_popup("補光提示", "請從 Android 螢幕頂部往下滑，開啟手電筒補光！"))
        main_layout.add_widget(torch_btn)

        # 2. 相機影像預覽區
        self.cam_image = Image(size_hint_y=None, height=220)
        main_layout.add_widget(self.cam_image)

        self.toggle_cam_btn = Button(
            text="📷 開啟/關閉相機鏡頭",
            size_hint_y=None, height=45,
            background_color=(0.01, 0.53, 0.82, 1)
        )
        self.toggle_cam_btn.bind(on_press=self.toggle_camera)
        main_layout.add_widget(self.toggle_cam_btn)

        # 3. 掃描結果與品項顯示
        prod_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        prod_layout.add_widget(Label(text="品項：", size_hint_x=0.25, color=(0, 0.9, 0.4, 1), bold=True))
        self.prod_display = TextInput(
            text="請對準條碼掃描或手動選擇",
            readonly=True, multiline=False, size_hint_x=0.75
        )
        prod_layout.add_widget(self.prod_display)
        main_layout.add_widget(prod_layout)

        # 4. 批號/效期區 (輸入框與快選)
        batch_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        batch_layout.add_widget(Label(text="批號效期：", size_hint_x=0.25, color=(0, 0.9, 0.4, 1), bold=True))
        self.batch_entry = TextInput(multiline=False, size_hint_x=0.75)
        batch_layout.add_widget(self.batch_entry)
        main_layout.add_widget(batch_layout)

        # 快選按鈕區
        self.batch_btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, spacing=5)
        main_layout.add_widget(self.batch_btn_layout)
        self.render_batch_buttons()

        # 5. 退貨原因下拉選單
        reason_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        reason_layout.add_widget(Label(text="退貨原因：", size_hint_x=0.25, color=(0, 0.9, 0.4, 1), bold=True))
        self.reason_spinner = Spinner(
            text="過期",
            values=("過期", "即期", "外觀瑕疵/損壞", "門市退貨"),
            size_hint_x=0.75
        )
        reason_layout.add_widget(self.reason_spinner)
        main_layout.add_widget(reason_layout)

        # 6. 數量顯示與九宮格大數字鍵盤
        qty_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=5)
        qty_layout.add_widget(Label(text="該堆數量：", size_hint_x=0.25, color=(0, 0.9, 0.4, 1), bold=True))
        self.qty_label = Label(
            text="0", font_size='22sp', bold=True,
            size_hint_x=0.75, color=(0, 0.9, 0.4, 1)
        )
        qty_layout.add_widget(self.qty_label)
        main_layout.add_widget(qty_layout)

        # 鍵盤 Grid
        grid_layout = GridLayout(cols=3, spacing=3, size_hint_y=None, height=180)
        buttons = [
            '7', '8', '9',
            '4', '5', '6',
            '1', '2', '3',
            '0', 'Clear', '⌫'
        ]
        for btn_text in buttons:
            btn = Button(text=btn_text, font_size='18sp', bold=True)
            btn.bind(on_press=lambda instance, t=btn_text: self.num_click(t))
            grid_layout.add_widget(btn)
        main_layout.add_widget(grid_layout)

        # 7. 提交與匯出按鈕
        submit_btn = Button(
            text="✅ 完成本堆錄入 (Save)",
            size_hint_y=None, height=45,
            background_color=(0.18, 0.49, 0.20, 1),
            bold=True
        )
        submit_btn.bind(on_press=self.save_record)
        main_layout.add_widget(submit_btn)

        export_btn = Button(
            text="📊 匯出 Excel 報表",
            size_hint_y=None, height=40,
            background_color=(0.08, 0.40, 0.75, 1),
            bold=True
        )
        export_btn.bind(on_press=self.export_excel)
        main_layout.add_widget(export_btn)

        return main_layout

    # --- 相機與畫面更新 ---
    def toggle_camera(self, instance):
        if self.is_camera_running:
            self.is_camera_running = False
            Clock.unschedule(self.update_camera_frame)
            if self.capture:
                self.capture.release()
                self.capture = None
            self.cam_image.texture = None
        else:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                self.show_popup("錯誤", "無法開啟相機，請確認系統權限！")
                return
            self.is_camera_running = True
            Clock.schedule_interval(self.update_camera_frame, 1.0 / 30.0)

    def update_camera_frame(self, dt):
        if not self.is_camera_running or not self.capture:
            return

        ret, frame = self.capture.read()
        if ret:
            # OpenCV 條碼解碼
            retval, decoded_info, decoded_type, points = barcode_detector.detectAndDecode(frame)
            if retval:
                for code in decoded_info:
                    if code:
                        if code in self.product_master:
                            prod_name = self.product_master[code]
                            self.prod_display.text = f"{prod_name} ({code})"
                        else:
                            self.handle_unknown_barcode(code)
                        break

            # 將 OpenCV 影像轉為 Kivy 紋理 (Texture) 渲染
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(dimensions=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.cam_image.texture = texture

    def handle_unknown_barcode(self, barcode):
        self.prod_display.text = f"未命名商品 ({barcode})"
        self.product_master[barcode] = f"未命名商品_{barcode[-4:]}"

    # --- UI 互動邏輯 ---
    def render_batch_buttons(self):
        self.batch_btn_layout.clear_widgets()
        self.batch_btn_layout.add_widget(Label(text="快選:", size_hint_x=0.2, color=(0.6, 0.6, 0.6, 1)))
        for b in self.history_batches[-3:]:
            btn = Button(text=b, size_hint_x=0.25)
            btn.bind(on_press=lambda instance, val=b: setattr(self.batch_entry, 'text', val))
            self.batch_btn_layout.add_widget(btn)

    def num_click(self, text):
        current = self.qty_label.text
        if text == "Clear":
            self.qty_label.text = "0"
        elif text == "⌫":
            self.qty_label.text = current[:-1] if len(current) > 1 else "0"
        else:
            if current == "0":
                self.qty_label.text = text
            else:
                self.qty_label.text = current + text

    def save_record(self, instance):
        prod_text = self.prod_display.text
        if "請對準條碼" in prod_text:
            self.show_popup("提示", "請先掃描條碼或輸入品項！")
            return

        prod_name = prod_text.split(" (")[0]
        barcode = prod_text.split("(")[1].replace(")", "") if "(" in prod_text else "N/A"
        batch = self.batch_entry.text.strip() or "未填"
        reason = self.reason_spinner.text
        qty = int(self.qty_label.text)

        if qty <= 0:
            self.show_popup("提示", "請輸入大於 0 的數量！")
            return

        record = {
            "時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "條碼": barcode,
            "品名": prod_name,
            "批號效期": batch,
            "退貨原因": reason,
            "數量": qty
        }
        self.records.append(record)

        if batch != "未填" and batch not in self.history_batches:
            self.history_batches.append(batch)
            self.render_batch_buttons()

        self.show_popup("成功", f"已錄入：\n{prod_name}\n數量：{qty} 件")
        self.qty_label.text = "0"

    def export_excel(self, instance):
        if not self.records:
            self.show_popup("提示", "目前沒有任何清點紀錄！")
            return

        df = pd.DataFrame(self.records)
        
        # 取得 Android App 內部私有寫入目錄，避免權限問題
        folder_path = self.user_data_dir
        filename = os.path.join(folder_path, f"退貨清冊_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

        try:
            df.to_excel(filename, index=False)
            self.show_popup("匯出成功", f"檔案已儲存至：\n{filename}")
        except Exception as e:
            self.show_popup("匯出失敗", f"錯誤：{str(e)}")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text="確定", size_hint_y=None, height=40)
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_stop(self):
        if self.capture:
            self.capture.release()


if __name__ == "__main__":
    ReturnQCApp().run()