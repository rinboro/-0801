# 必要なライブラリをインポート
import PySimpleGUI as sg  # GUIを作成するためのライブラリ
import json  # JSONデータの処理用
import os  # ファイル操作用
from datetime import datetime  # 日時処理用

# メモを保存するJSONファイルの名前を定義
MEMO_FILE = 'memos.json'

def create_window(memos):
    """
    メインウィンドウを作成する関数
    :param memos: メモのリスト
    :return: PySimpleGUIのウィンドウオブジェクト
    """
    layout = [
        # メモ入力欄と追加ボタン
        [sg.Text('メモ:'), sg.InputText(key='-MEMO-'), sg.Button('追加')],
        # 検索欄と検索ボタン
        [sg.Text('検索:'), sg.InputText(key='-SEARCH-'), sg.Button('検索')],
        # メモリスト表示領域
        [sg.Listbox(values=get_memo_list(memos), size=(50, 10), key='-MEMOLIST-')],
        # 操作ボタン群
        [sg.Button('編集'), sg.Button('削除'), sg.Button('並べ替え'), sg.Button('終了')]
    ]
    return sg.Window('メモアプリ', layout)

def get_memo_list(memos):
    """
    メモリストを表示用の文字列リストに変換する関数
    :param memos: メモのリスト
    :return: 表示用の文字列リスト
    """
    # 各メモの日付と内容（先頭30文字）を組み合わせた文字列のリストを返す
    return [f"{memo['date']} - {memo['content'][:30]}..." for memo in memos]

def load_memos():
    """
    JSONファイルからメモを読み込む関数
    :return: メモのリスト（読み込みに失敗した場合は空リスト）
    """
    try:
        if os.path.exists(MEMO_FILE):
            with open(MEMO_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():  # ファイルが空でない場合
                    return json.loads(content)
                else:
                    print("メモファイルが空です。新しいメモリストを作成します。")
        else:
            print("メモファイルが見つかりません。新しいファイルを作成します。")
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}")
        print("メモファイルの内容が無効です。新しいメモリストを作成します。")
    except Exception as e:
        print(f"ファイル読み込みエラー: {e}")
    
    return []  # エラーが発生した場合や、ファイルが存在しない/空の場合は空のリストを返す

def save_memos(memos):
    """
    メモをJSONファイルに保存する関数
    :param memos: 保存するメモのリスト
    """
    with open(MEMO_FILE, 'w', encoding='utf-8') as f:
        json.dump(memos, f, ensure_ascii=False, indent=2)

def add_memo(memos, content):
    """
    新しいメモをリストに追加する関数
    :param memos: 既存のメモリスト
    :param content: 追加するメモの内容
    :return: 更新されたメモリスト
    """
    memos.append({
        'content': content,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 現在の日時を文字列として保存
    })
    return memos

def edit_memo(memo):
    """
    メモを編集するための小ウィンドウを表示する関数
    :param memo: 編集対象のメモ
    :return: 編集後のメモ
    """
    layout = [
        [sg.Text('メモ内容:')],
        [sg.Multiline(memo['content'], size=(50, 5), key='-CONTENT-')],
        [sg.Button('保存'), sg.Button('キャンセル')]
    ]
    window = sg.Window('メモ編集', layout)
    event, values = window.read()
    window.close()
    if event == '保存':
        memo['content'] = values['-CONTENT-']
        memo['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 編集日時を更新
    return memo

def main():
    """
    メインの実行関数
    """
    memos = load_memos()  # メモを読み込む
    window = create_window(memos)  # メインウィンドウを作成

    while True:
        event, values = window.read()  # イベントとその値を取得

        if event == sg.WINDOW_CLOSED or event == '終了':
            save_memos(memos)  # メモを保存して終了
            break

        if event == '追加':
            memo = values['-MEMO-']
            if memo:
                memos = add_memo(memos, memo)  # 新しいメモを追加
                window['-MEMOLIST-'].update(get_memo_list(memos))  # リスト表示を更新
                window['-MEMO-'].update('')  # 入力欄をクリア
                save_memos(memos)  # メモを保存

        if event == '検索':
            search_term = values['-SEARCH-']
            if search_term:
                # 検索語を含むメモをフィルタリング
                matched_memos = [memo for memo in memos if search_term.lower() in memo['content'].lower()]
                window['-MEMOLIST-'].update(get_memo_list(matched_memos))
            else:
                window['-MEMOLIST-'].update(get_memo_list(memos))  # 全メモを表示

        if event == '編集':
            selected_indices = window['-MEMOLIST-'].get_indexes()
            if selected_indices:
                index = selected_indices[0]
                memos[index] = edit_memo(memos[index])  # 選択されたメモを編集
                window['-MEMOLIST-'].update(get_memo_list(memos))  # リスト表示を更新
                save_memos(memos)  # 変更を保存

        if event == '削除':
            selected_indices = window['-MEMOLIST-'].get_indexes()
            if selected_indices:
                confirm = sg.popup_yes_no('選択したメモを削除しますか？', title='確認')
                if confirm == 'Yes':
                    # 選択されていないメモだけを残す
                    memos = [memo for i, memo in enumerate(memos) if i not in selected_indices]
                    window['-MEMOLIST-'].update(get_memo_list(memos))  # リスト表示を更新
                    save_memos(memos)  # 変更を保存

        if event == '並べ替え':
            # メモを日付の降順で並べ替え
            memos.sort(key=lambda x: x['date'], reverse=True)
            window['-MEMOLIST-'].update(get_memo_list(memos))  # リスト表示を更新

    window.close()  # ウィンドウを閉じる

if __name__ == '__main__':
    main()  # メイン関数を実行
