"""
Curated historical blockchain transactions for demo cases (Ronin, Poly Network, Wormhole).
Used as instant offline / fallback seed data when live blockchain API rate limits or is offline.
All addresses are stored normalized to lowercase to prevent case-mismatch graph fragmentation.
"""

CURATED_SEEDS = {
    "Ronin Bridge Hack ($600M, 2022)": [
        # Lazarus hacker wallet -> intermediary hubs -> peel chains & Tornado Cash routers
        {"from": "0x098b716b8aaf21512996dc57eb0615e2383e2f96", "to": "0x8c75ad518dce956b488ab65e36ab229d8664bf29", "value": 200.0, "hash": "0xronin_1"},
        {"from": "0x098b716b8aaf21512996dc57eb0615e2383e2f96", "to": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b", "value": 100.0, "hash": "0xronin_2"}, # Tornado Router
        {"from": "0x098b716b8aaf21512996dc57eb0615e2383e2f96", "to": "0xe129927cfc61ce2f0b2a0ca6d8f9482d4ee60c64", "value": 50.0, "hash": "0xronin_3"},
        {"from": "0x098b716b8aaf21512996dc57eb0615e2383e2f96", "to": "0xfc3ff9d9abd3abadda68821e443779beb1082f43", "value": 10.0, "hash": "0xronin_4"},
        {"from": "0x098b716b8aaf21512996dc57eb0615e2383e2f96", "to": "0xbc25d517cc9d7ea453622ded3213302de34d29eb", "value": 5.0, "hash": "0xronin_5"},
        # Peel Chain pattern: 8c75ad sends 180 to main and 10 to peel
        {"from": "0x8c75ad518dce956b488ab65e36ab229d8664bf29", "to": "0x4e5b2e1dc63f6b91cb6cd759936495434c7e972f", "value": 180.0, "hash": "0xronin_6"},
        {"from": "0x8c75ad518dce956b488ab65e36ab229d8664bf29", "to": "0xdf225c04450504e9198569982c98de2e15b9df2a", "value": 10.0, "hash": "0xronin_7"},
        # Fan-out pattern from 4e5b2e
        {"from": "0x4e5b2e1dc63f6b91cb6cd759936495434c7e972f", "to": "0x1111111254fb6c44bac0bed2854e76f90643097d", "value": 35.0, "hash": "0xronin_8"},
        {"from": "0x4e5b2e1dc63f6b91cb6cd759936495434c7e972f", "to": "0x2222222222222222222222222222222222222222", "value": 35.0, "hash": "0xronin_9"},
        {"from": "0x4e5b2e1dc63f6b91cb6cd759936495434c7e972f", "to": "0x3333333333333333333333333333333333333333", "value": 35.0, "hash": "0xronin_10"},
        {"from": "0x4e5b2e1dc63f6b91cb6cd759936495434c7e972f", "to": "0x4444444444444444444444444444444444444444", "value": 35.0, "hash": "0xronin_11"},
        {"from": "0x4e5b2e1dc63f6b91cb6cd759936495434c7e972f", "to": "0x5555555555555555555555555555555555555555", "value": 35.0, "hash": "0xronin_12"},
        # Circular flow: e12992 -> f1 -> f2 -> e12992
        {"from": "0xe129927cfc61ce2f0b2a0ca6d8f9482d4ee60c64", "to": "0x6666666666666666666666666666666666666666", "value": 15.0, "hash": "0xronin_13"},
        {"from": "0x6666666666666666666666666666666666666666", "to": "0x7777777777777777777777777777777777777777", "value": 14.5, "hash": "0xronin_14"},
        {"from": "0x7777777777777777777777777777777777777777", "to": "0xe129927cfc61ce2f0b2a0ca6d8f9482d4ee60c64", "value": 14.0, "hash": "0xronin_15"},
    ],

    "Poly Network Hack ($611M, 2021)": [
        {"from": "0xc8a65fadf0e0ddaf421f28feab69bf6e2e589963", "to": "0x5c4242be2a7c7936a7387d12d1d471609277873a", "value": 1000.0, "hash": "0xpoly_1"},
        {"from": "0xc8a65fadf0e0ddaf421f28feab69bf6e2e589963", "to": "0x0b36cc681301e7e475b58452034466d400793364", "value": 500.0, "hash": "0xpoly_2"},
        {"from": "0xc8a65fadf0e0ddaf421f28feab69bf6e2e589963", "to": "0x250e76987d838a75310c34bf422ea9f1ac4cc906", "value": 250.0, "hash": "0xpoly_3"},
        {"from": "0x5c4242be2a7c7936a7387d12d1d471609277873a", "to": "0x8888888888888888888888888888888888888888", "value": 450.0, "hash": "0xpoly_4"},
        {"from": "0x5c4242be2a7c7936a7387d12d1d471609277873a", "to": "0x9999999999999999999999999999999999999999", "value": 40.0, "hash": "0xpoly_5"},
        {"from": "0x0b36cc681301e7e475b58452034466d400793364", "to": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "value": 100.0, "hash": "0xpoly_6"},
        {"from": "0x0b36cc681301e7e475b58452034466d400793364", "to": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "value": 100.0, "hash": "0xpoly_7"},
        {"from": "0x0b36cc681301e7e475b58452034466d400793364", "to": "0xcccccccccccccccccccccccccccccccccccccccc", "value": 100.0, "hash": "0xpoly_8"},
        {"from": "0x0b36cc681301e7e475b58452034466d400793364", "to": "0xdddddddddddddddddddddddddddddddddddddddd", "value": 100.0, "hash": "0xpoly_9"},
    ],

    "Wormhole Bridge Hack ($321M, 2022)": [
        {"from": "0x629e7da20197a5429d30da36e77d06cdf796b71a", "to": "0x0048e99a566d6641d9395074294f56b47b203cfc", "value": 5000.0, "hash": "0xworm_1"},
        {"from": "0x629e7da20197a5429d30da36e77d06cdf796b71a", "to": "0x271089d3030da8446422202010134706785424c8", "value": 3000.0, "hash": "0xworm_2"},
        {"from": "0x629e7da20197a5429d30da36e77d06cdf796b71a", "to": "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc", "value": 1000.0, "hash": "0xworm_3"},
        {"from": "0x0048e99a566d6641d9395074294f56b47b203cfc", "to": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "value": 4500.0, "hash": "0xworm_4"},
        {"from": "0x0048e99a566d6641d9395074294f56b47b203cfc", "to": "0xffffffffffffffffffffffffffffffffffffffff", "value": 400.0, "hash": "0xworm_5"},
        {"from": "0x271089d3030da8446422202010134706785424c8", "to": "0x1212121212121212121212121212121212121212", "value": 500.0, "hash": "0xworm_6"},
        {"from": "0x271089d3030da8446422202010134706785424c8", "to": "0x2323232323232323232323232323232323232323", "value": 500.0, "hash": "0xworm_7"},
        {"from": "0x271089d3030da8446422202010134706785424c8", "to": "0x3434343434343434343434343434343434343434", "value": 500.0, "hash": "0xworm_8"},
        {"from": "0x271089d3030da8446422202010134706785424c8", "to": "0x4545454545454545454545454545454545454545", "value": 500.0, "hash": "0xworm_9"},
    ],

    "Euler Finance Exploit ($197M, 2023)": [
        {"from": "0xb66cd966670d962c227b3eaba30a872dbfb995db", "to": "0x8888888825f385c7d812328bb0fb443f3d6c1411", "value": 2500.0, "hash": "0xeuler_1"},
        {"from": "0xb66cd966670d962c227b3eaba30a872dbfb995db", "to": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b", "value": 1000.0, "hash": "0xeuler_2"},
        {"from": "0xb66cd966670d962c227b3eaba30a872dbfb995db", "to": "0x9999999936cc17e475b58452034466d400793364", "value": 800.0, "hash": "0xeuler_3"},
        # Peel Chain: 88888888 -> 2200 main, 250 peel
        {"from": "0x8888888825f385c7d812328bb0fb443f3d6c1411", "to": "0x77777777a7c7936a7387d12d1d471609277873a1", "value": 2200.0, "hash": "0xeuler_4"},
        {"from": "0x8888888825f385c7d812328bb0fb443f3d6c1411", "to": "0x66666666df0e0ddaf421f28feab69bf6e2e58996", "value": 250.0, "hash": "0xeuler_5"},
        # Fan-out layer
        {"from": "0x77777777a7c7936a7387d12d1d471609277873a1", "to": "0x111122223333444455556666777788889999aaaa", "value": 500.0, "hash": "0xeuler_6"},
        {"from": "0x77777777a7c7936a7387d12d1d471609277873a1", "to": "0x22223333444455556666777788889999aaaabbbb", "value": 500.0, "hash": "0xeuler_7"},
        {"from": "0x77777777a7c7936a7387d12d1d471609277873a1", "to": "0x3333444455556666777788889999aaaabbbbcccc", "value": 500.0, "hash": "0xeuler_8"},
        {"from": "0x77777777a7c7936a7387d12d1d471609277873a1", "to": "0x444455556666777788889999aaaabbbbccccdddd", "value": 500.0, "hash": "0xeuler_9"},
    ],

    "Nomad Bridge Hack ($190M, 2022)": [
        {"from": "0xa5c45e07cfa66784742931720ddc9f2441ed01c1", "to": "0xbbbbbbbb742931720ddc9f2441ed01c131720ddc", "value": 3500.0, "hash": "0xnomad_1"},
        {"from": "0xa5c45e07cfa66784742931720ddc9f2441ed01c1", "to": "0xcccccccc0048e99a566d6641d9395074294f56b4", "value": 1800.0, "hash": "0xnomad_2"},
        # Crowd-looting dispersion (fan-out pattern to copy-cat wallets)
        {"from": "0xbbbbbbbb742931720ddc9f2441ed01c131720ddc", "to": "0x5555666677778888999900001111222233334444", "value": 600.0, "hash": "0xnomad_3"},
        {"from": "0xbbbbbbbb742931720ddc9f2441ed01c131720ddc", "to": "0x6666777788889999000011112222333344445555", "value": 600.0, "hash": "0xnomad_4"},
        {"from": "0xbbbbbbbb742931720ddc9f2441ed01c131720ddc", "to": "0x7777888899990000111122223333444455556666", "value": 600.0, "hash": "0xnomad_5"},
        {"from": "0xbbbbbbbb742931720ddc9f2441ed01c131720ddc", "to": "0x8888999900001111222233334444555566667777", "value": 600.0, "hash": "0xnomad_6"},
        {"from": "0xbbbbbbbb742931720ddc9f2441ed01c131720ddc", "to": "0x9999000011112222333344445555666677778888", "value": 600.0, "hash": "0xnomad_7"},
        # Circular flow test
        {"from": "0xcccccccc0048e99a566d6641d9395074294f56b4", "to": "0xaaaa1111bbbb2222cccc3333dddd4444eeee5555", "value": 450.0, "hash": "0xnomad_8"},
        {"from": "0xaaaa1111bbbb2222cccc3333dddd4444eeee5555", "to": "0xcccccccc0048e99a566d6641d9395074294f56b4", "value": 445.0, "hash": "0xnomad_9"},
    ],

    "FTX Accounts Drainer ($477M, 2022)": [
        {"from": "0x59abf3837fa962d6853b4cc0a19513aa031fd32b", "to": "0x3939393939393939393939393939393939393939", "value": 8500.0, "hash": "0xftx_1"},
        {"from": "0x59abf3837fa962d6853b4cc0a19513aa031fd32b", "to": "0x4848484848484848484848484848484848484848", "value": 4200.0, "hash": "0xftx_2"},
        {"from": "0x59abf3837fa962d6853b4cc0a19513aa031fd32b", "to": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b", "value": 2000.0, "hash": "0xftx_3"},
        # Peel Chain: 39393939 -> 7500 main, 800 peel
        {"from": "0x3939393939393939393939393939393939393939", "to": "0x5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a", "value": 7500.0, "hash": "0xftx_4"},
        {"from": "0x3939393939393939393939393939393939393939", "to": "0x6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b6b", "value": 800.0, "hash": "0xftx_5"},
        # Dispersion layer
        {"from": "0x5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a", "to": "0x7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c", "value": 1500.0, "hash": "0xftx_6"},
        {"from": "0x5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a", "to": "0x8d8d8d8d8d8d8d8d8d8d8d8d8d8d8d8d8d8d8d8d", "value": 1500.0, "hash": "0xftx_7"},
        {"from": "0x5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a", "to": "0x9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e", "value": 1500.0, "hash": "0xftx_8"},
        {"from": "0x5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a", "to": "0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f", "value": 1500.0, "hash": "0xftx_9"},
    ]
}
