# Example 1
Invoking: `chat_with_db` with `{'english_input': 'Which banker has the most number of clients?'}`


SELECT Name, COUNT(Client_ID) AS Number_of_Clients
FROM accounts
JOIN bankers ON accounts.Banker_ID = bankers.ID
GROUP BY Banker_ID
ORDER BY Number_of_Clients DESC
LIMIT 1;
            Name  Number_of_Clients
0  Sherri Walter               1149


# Example 2:
Invoking: `chat_with_db` with `{'english_input': 'List the top 10 bankers with the most number of clients.', 'client_name': ''}`


SELECT b.ID, b.Name, COUNT(l.Client_1) AS Num_Clients
FROM bankers b
JOIN links l ON b.ID = l.Client_1
GROUP BY b.ID
ORDER BY Num_Clients DESC
LIMIT 10;
   ID               Name  Num_Clients
0  32       John Hoffman            4
1  59  Monique Henderson            3
2  56    Kathleen Cannon            3
3  34       Rachael Ross            3
4  22        Jason Adams            3
5  11        Linda Wolfe            3
6  57      David Alvarez            2
7  49       Alyssa Smith            2
8  44         Guy Gaines            2
9  41     Allison Maddox            2


Invoking: `chat_with_db` with `{'english_input': 'List the top 10 bankers with the most number of clients using only the accounts and clients table.', 'client_name': ''}`


SELECT b.Name AS Banker_Name, COUNT(a.Client_ID) AS Number_of_Clients
FROM accounts a
JOIN bankers b ON a.Banker_ID = b.ID
GROUP BY b.Name
ORDER BY Number_of_Clients DESC
LIMIT 10;
         Banker_Name  Number_of_Clients
0      Sherri Walter               1149
1  Christine Hensley                963
2       John Hoffman                961
3        Jill Rhodes                932
4         Jose Mason                930
5       Keith Miller                803
6    Patricia Miller                797
7       Alyssa Smith                757
8   Danielle Johnson                750
9   Anthony Gonzalez                558


# Example 3:
> Entering new AgentExecutor chain...

Invoking: `chat_with_db` with `{'english_input': 'List the top 10 clients of banker Alyssa Smith along with their names, number of accounts, products, and balances since 2019.', 'client_name': 'Alyssa Smith'}`


SELECT c.ID, c.Name, COUNT(a.ID) AS Number_of_Accounts, a.Product_Group AS Products, SUM(a.Balance) AS Balances
FROM clients c
JOIN accounts a ON c.ID = a.Client_ID
JOIN bankers b ON a.Banker_ID = b.ID
WHERE b.Name = 'Alyssa Smith' AND a.Start_Dt >= '2019'
GROUP BY c.ID
ORDER BY Balances DESC
LIMIT 10;
     ID                     Name  Number_of_Accounts Products    Balances
0  4965           Johnson-Norman                   1   Wealth  58461548.8
1  3583                Denise Le                   1   Wealth  45928436.0
2  6557            Burton-Garcia                   1   Wealth  39942522.6
3  9916               Graham LLC                   1   Wealth  38113352.7
4  5299              Jackson Ltd                   1   Wealth  38028898.6
5  9153  Reese, Pineda and Smith                   1   Wealth  35708300.6
6  8399            Deborah Fritz                   1   Wealth  32900912.7
7  4325           Jennifer Giles                   1   Wealth  30141464.4
8  6045             Copeland Inc                   1   Wealth  28853794.8
9  8595                 Cole LLC                   1   Wealth  20974381.6

# Example 4

Invoking: `chat_with_db` with `{'english_input': 'List the members of Jennifer Giles household and their relationship with her.', 'client_name': 'Jennifer Giles'}`


SELECT c.ID, c.Name, l.Link_Type
FROM clients c
JOIN links l ON c.ID = l.Client_1 OR c.ID = l.Client_2
WHERE l.Household_ID = (SELECT Household_ID FROM links WHERE Client_1 = (SELECT ID FROM clients WHERE Name = 'Jennifer Giles') OR Client_2 = (SELECT ID FROM clients WHERE Name = 'Jennifer Giles'))
AND c.ID <> (SELECT ID FROM clients WHERE Name = 'Jennifer Giles')
LIMIT 10;
     ID              Name Link_Type
0  4324  Lawrence Johnson    Spouse