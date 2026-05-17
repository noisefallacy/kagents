# Doc Search Test Prompts

`doc_search` 用のテストプロンプト集です。

対象データ:
- [sample_notes.md](C:/Users/kagin/kagents/data/docs/sample_notes.md)
- [inbox_update.eml](C:/Users/kagin/kagents/data/docs/inbox_update.eml)
- [quarterly_numbers.xlsx](C:/Users/kagin/kagents/data/docs/quarterly_numbers.xlsx)

## 基本

```text
budget forecast について書かれている内容を教えて
```

期待:
- `sample_notes.md`
- `inbox_update.eml`
- `quarterly_numbers.xlsx`
  のいずれかに触れる

```text
revenue planning に関する情報を探してください
```

期待:
- `sample_notes.md`
- `quarterly_numbers.xlsx`
  に触れる

## 自然文

```text
finance チーム向けに何をレビューする必要がありますか
```

期待:
- `inbox_update.eml` を参照する

```text
四半期の数値や planning に関する内容を教えて
```

期待:
- `quarterly_numbers.xlsx` を参照する

## 見つからないケース

```text
契約書番号を教えて
```

期待:
- 根拠が見つからないと返す
