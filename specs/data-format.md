# Entry Definition

- Each entry always contains a date (YYYY/MM/DD). e.g., `2025/04/01`.
- Each entry always contains a specific currency. e.g., `SEK`.
- Each entry always contains a category. The category can contain spaces/multiple words. e.g., `Base & Recurring`.
- An accounting entry can be of two types, Expense or Income.
- Each entry can contain multiple entry items, but an entry must contain at least one entry item.

# Entry Line Definition

- Each entry line always refers to the same currency as its parent Entry. e.g., `SEK`.
- Each entry line always contains an integer, positive and greater than 0 amount, e.g., `100`.
- Each entry line always contains a description. The description cannot contain spaces, using instead colons (`:`) to separate multiple words. e.g., `Expenses:Shopping:Food`.
  - If the parent entry is of type Income, all the entry lines inside it must have the exact same description. Otherwhise they would need to go in separate entries.
  - If the parent entry is of type Expense, each entry line can have a different description.
- New entry lines can be added to an existing entry, as long as:
  - The date fully matches (both entry types)
  - If the entry type is Income, the description also fully matches


# .dat File Format

- There is one file per country, year, and month, with extension `.dat`. Format is `<country>-YYYY-MM.dat`, e.g. `se-2025-04.dat`.
- The file country defines the currency of entreies contained in it. e.g., `se-` file -> `SEK` currency, `es-` file -> `EUR` currency.
- Each file can contain [1, N] entries.
- Entries insie a file are ordered by date descending (entries with newer dates will be last in the file).
- Each entry can be of either type: Expense or Income.
- Each entry follows the entry definition.
- Each entry line follows the entry line definition.

- The format of writing an entry of type Expense is as follows:
```
<entry-date> <entry-category>
  <entry-line-description>               <currency> <entry-line-amount>
  <entry-line-description>               <currency> <entry-line-amount>
  * Assets:Checking

```
Example:
```
2025/04/05 Base & Recurring
  Expenses:House:Mortage                 EUR 300
  Expenses:House:Electricity             EUR 20
  * Assets:Checking

```
- After an entry, there is always a blank line.
- Expense-type entries always contain a last line with `* Assets:Checking`.
- Between entry line descriptions and the currency there will be `(39 - <entry-line-description> length)` spaces.
- Between the currency and the amount there is always a single space.

- The format of writing an entry of type Income is as follows:
```
<entry-date> <entry-category>
  * Assets:Checking                      <currency> <entry-line-amount>
  * Assets:Checking                      <currency> <entry-line-amount>
  <entry-line-description>

```
Example:
```
2025/04/05 Employer
  * Assets:Checking                      € 1000
  * Assets:Checking                      € 500
  Income:Employer:SalaryAndBonus

```
- After an entry, there is always a blank line.
- Income-type entries always contain per line: `* Assets:Checking`, then the currency and then the amount.
- Between entry line's `* Assets:Checking` and the currency there will be 22 spaces.
- Between the currency and the amount there is always a single space.
- Income-type entries always contain a last line with the entry line description.
- There can be multiple Expense-type entries with the same date, as long as the category differs.
- There should be at most one Income-type entry for a specific date.
- Income entries can be merged with existing entries of the same date if they have the same description.
