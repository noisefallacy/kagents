# Portfolio Manager Test Prompts

`portfolio_manager` 用のシンプルなテストプロンプト集です。

対象データ:
- [sample_notes.md](C:/Users/kagin/kagents/data/docs/sample_notes.md)
- [quarterly_numbers.xlsx](C:/Users/kagin/kagents/data/docs/quarterly_numbers.xlsx)
- [inbox_update.eml](C:/Users/kagin/kagents/data/docs/inbox_update.eml)

## 基本

```text
今の優先事項を教えて
```

期待:
- `sample_notes.md` の next steps に触れる

```text
今の予算まわりで確認すべきことは何ですか
```

期待:
- `inbox_update.eml`
- `quarterly_numbers.xlsx`
  に触れる

## 自然文

```text
finance チーム向けに何を準備する必要がありますか
```

期待:
- `budget forecast`
- `revenue planning assumptions`
  に触れる

```text
木曜日までにやることはありますか
```

期待:
- `budget forecast` のレビューに触れる

## 要約

```text
この案件の次のアクションをまとめて
```

期待:
- 文書とメールの内容を短くまとめる

## J-Quants API

```text
7203 の 2026-03-14 の終値を教えて
```

期待:
- `get_jquants_daily_quote` を使う
- 4桁コードを 5桁に正規化して取得する

```text
トヨタの株価を見たいです。コードは 7203 です。2026-03-14 の日足を教えて
```

期待:
- J-Quants API を使う
- Open / High / Low / Close のいずれかに触れる

## Web Search

```text
今日のトヨタに関する最新ニュースを教えて
```

期待:
- Google Search を使う
- Web の出典に触れる

```text
直近の日本株市場の話題を簡単にまとめて
```

期待:
- 最新性が必要なので Google Search を使う
- ローカル文書ではなく外部情報を使う

## 見つからないケース

```text
契約書番号を教えて
```

期待:
- 根拠が見つからないと返す
