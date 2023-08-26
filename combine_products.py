### This standalone script is used to find the cheapest combination of products that cover all components of a Pixhawk system

from pyperclip import copy
import sys

from util import clearConsole

command_line_args = sys.argv[1:]

if "-h" in command_line_args or "--help" in command_line_args:
    print("Command line arguments:")
    print("-h, --help:\t\t\tShow this help message")

    print("-n, --number:\t\t\tNumber of top (unmerged) combinations to output")
    
    print("-s, --skip-merge:\t\tDon't merge combinations which contain the same category of products")
    print("-b, --both:\t\t\tOutput both the merged and the unmerged combinations, concatenated")
    print("-p, --parsed-combinations:\tDon't recombine the products, use the cached combinations saved in the code as a list")
    
    print("-d, --dont-clear:\t\tDon't clear the console before running")
    
    sys.exit()

dontMergeJustConvert = "-s" in command_line_args or "--skip-merge" in command_line_args
bothMergedAndUnmerged = "-b" in command_line_args or "--both" in command_line_args
use_parsed_combinations = "-p" in command_line_args or "--parsed-combinations" in command_line_args
number_of_combinations = (
    int(command_line_args[command_line_args.index("-n") + 1])
    if ("-n" in command_line_args or "--number" in command_line_args)
    else None)

if dontMergeJustConvert and bothMergedAndUnmerged:
    print("Can't use both -s/--skip-merge and -b/--both at the same time")
    sys.exit()

if "-d" not in command_line_args and "--dont-clear" not in command_line_args:
    clearConsole()

# headers: price, delivery date, Pixhawk, GPS, power module, IIC splitter, PPM decoder, buzzer, safety switch, micro SD
raw = """
1	gps	https://www.ebay.com/itm/201723332948		 $20,05 	 $20,05 	 $0,99 	 $0,99 	 $21,04 	aug 18–aug 25		TRUE										
2	gps	https://www.ebay.com/itm/204355711714		 EUR18,2 	 $20,00 	 $-   	 $-   	 $20,00 	aug 31–szept 28		TRUE										
3	IIC splitter	https://www.ebay.com/itm/123772651468		 EUR3,87 	 $4,25 	 EUR0,50 	 $0,55 	 $4,80 	aug 18–aug 25				TRUE								
4	IIC splitter	https://www.ebay.com/itm/125403536735		 EUR3,87 	 $4,25 	 EUR0,50 	 $0,55 	 $4,80 	aug 18–aug 25				TRUE								
5	IIC splitter	https://www.ebay.com/itm/154627344701		 EUR4,02 	 $4,42 	 EUR0,50 	 $0,55 	 $4,97 	aug 18–aug 25				TRUE								
6	IIC splitter	https://www.ebay.com/itm/154660911645		 AUD10,64 	 $7,00 	 $-   	 $-   	 $7,00 	aug 18–aug 25				TRUE								
7	IIC splitter	https://www.ebay.com/itm/165386772432		 EUR4,01 	 $4,41 	 EUR0,50 	 $0,55 	 $4,96 	aug 18–aug 25				TRUE								
8	IIC splitter	https://www.ebay.com/itm/165489612954		 AUD11,66 	 $7,67 	 $-   	 $-   	 $7,67 	aug 18–aug 25				TRUE								
9	IIC splitter	https://www.ebay.com/itm/255436257992		 EUR3,87 	 $4,25 	 EUR0,50 	 $0,55 	 $4,80 	aug 18–aug 25				TRUE								
10	IIC splitter	https://www.ebay.com/itm/255616205778		 EUR3,87 	 $4,25 	 EUR0,50 	 $0,55 	 $4,80 	aug 18–aug 25				TRUE								
11	IIC splitter	https://www.ebay.com/itm/274724049454		 GBP3,04 	 $3,90 	 $-   	 $-   	 $3,90 	szept 4–okt 2				TRUE								
12	IIC splitter	https://www.ebay.com/itm/284466362618		 EUR4 	 $4,40 	 EUR0,50 	 $0,55 	 $4,95 	aug 18–aug 25				TRUE								
13	IIC splitter	https://www.ebay.com/itm/295001465675		 EUR3,94 	 $4,33 	 EUR0,50 	 $0,55 	 $4,88 	aug 18–aug 25				TRUE								
14	IIC splitter	https://www.ebay.com/itm/401598943536		 EUR4,06 	 $4,46 	 EUR1,00 	 $1,10 	 $5,56 	aug 18–aug 25				TRUE								
15	IIC splitter	https://www.ebay.com/itm/401598945073		 EUR4,95 	 $5,44 	 EUR0,50 	 $0,55 	 $5,99 	aug 18–aug 25				TRUE								
16	IIC splitter	https://www.ebay.com/itm/402704631715		 EUR4,01 	 $4,41 	 EUR0,50 	 $0,55 	 $4,96 	aug 18–aug 25				TRUE								
17	LED+USB	https://www.ebay.com/itm/152836486311		 EUR7,99 	 $8,78 	 $-   	 $-   	 $8,78 	aug 24–aug 31												TRUE
18	LED+USB	https://www.ebay.com/itm/255055738101		 $9,04 	 $9,04 	 $-   	 $-   	 $9,04 	aug 24–aug 31												TRUE
19	LED+USB	https://www.ebay.com/itm/256147868144		 EUR7,99 	 $8,78 	 $-   	 $-   	 $8,78 	aug 24–aug 31												TRUE
20	LED+USB	https://www.ebay.com/itm/275244037371		 EUR7,99 	 $8,78 	 $-   	 $-   	 $8,78 	szept 6–okt 4												TRUE
21	LED+USB	https://www.ebay.com/itm/354834215723		 EUR7,99 	 $8,78 	 $-   	 $-   	 $8,78 	aug 24–aug 31												TRUE
22	Pixhawk	https://www.ebay.com/itm/175739246655		 $120,00 	 $120,00 	 $31,67 	 $31,67 	 $151,67 	aug 30–szept 11	TRUE											
23	power module	https://www.ebay.com/itm/311852214732		 $5,03 	 $5,03 	 $0,99 	 $0,99 	 $6,02 	aug 18–aug 25			TRUE									
24	power module	https://www.ebay.com/itm/314076540299	T plug	 $5,98 	 $5,98 	 $0,99 	 $0,99 	 $6,97 	aug 18–aug 25			TRUE									
25	power module	https://www.ebay.com/itm/314076540299	XT60	 $5,98 	 $5,98 	 $0,99 	 $0,99 	 $6,97 	aug 18–aug 25			TRUE									
26	szett	https://www.ebay.com/itm/125094437332		 $118,01 	 $118,01 	 $3,00 	 $3,00 	 $121,01 	aug 28–szept 4	TRUE					TRUE	TRUE					
27	szett	https://www.ebay.com/itm/125249976612		 $119,27 	 $119,27 	 $3,00 	 $3,00 	 $122,27 	aug 28–szept 4	TRUE					TRUE	TRUE					
28	szett	https://www.ebay.com/itm/125282686948		 $148,08 	 $148,08 	 $-   	 $-   	 $148,08 	aug 28–szept 4	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE			TRUE	TRUE	
29	szett	https://www.ebay.com/itm/125282688385		 $103,08 	 $103,08 	 $-   	 $-   	 $103,08 	aug 28–szept 4	TRUE			TRUE	TRUE	TRUE	TRUE			TRUE		
30	szett	https://www.ebay.com/itm/155463945805	without GPS	 $118,23 	 $118,23 	 $8,69 	 $8,69 	 $126,92 	aug 24–aug 31	TRUE			TRUE	TRUE	TRUE	TRUE					
31	szett	https://www.ebay.com/itm/155463945805	with M8N GPS	 $148,08 	 $148,08 	 $8,69 	 $8,69 	 $156,77 	aug 24–aug 31	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE				TRUE	
32	szett	https://www.ebay.com/itm/165458160410		 $100,00 	 $100,00 	 $5,00 	 $5,00 	 $105,00 	aug 31–szept 7	TRUE			TRUE	TRUE	TRUE	TRUE			TRUE		
33	szett	https://www.ebay.com/itm/165467595797	Option 1	 $103,08 	 $103,08 	 $25,00 	 $25,00 	 $128,08 	aug 25–szept 1	TRUE			TRUE	TRUE	TRUE	TRUE			TRUE		
34	szett	https://www.ebay.com/itm/165467595797	Option 2	 $145,61 	 $145,61 	 $25,00 	 $25,00 	 $170,61 	aug 25–szept 1	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE			TRUE	TRUE	
35	szett	https://www.ebay.com/itm/173981292247	Style B (!felcsrélték)	 $90,84 	 $90,84 	 $27,00 	 $27,00 	 $117,84 	aug 23–aug 30	TRUE			TRUE	TRUE	TRUE	TRUE			TRUE		
36	szett	https://www.ebay.com/itm/173981292247	Style A (!felcsrélték)	 $116,42 	 $116,42 	 $27,00 	 $27,00 	 $143,42 	aug 23–aug 30	TRUE					TRUE	TRUE			TRUE		
37	szett	https://www.ebay.com/itm/175328606075		 $117,65 	 $117,65 	 $8,69 	 $8,69 	 $126,34 	aug 28–szept 4	TRUE			TRUE		TRUE	TRUE					
38	szett	https://www.ebay.com/itm/175429824406	Black	 $116,42 	 $116,42 	 $27,00 	 $27,00 	 $143,42 	aug 23–aug 30	TRUE					TRUE	TRUE			TRUE		
39	szett	https://www.ebay.com/itm/175429824406	White	 $116,58 	 $116,58 	 $27,00 	 $27,00 	 $143,58 	aug 23–aug 30	TRUE					TRUE	TRUE			TRUE		
40	szett	https://www.ebay.com/itm/175430717105		 $111,91 	 $111,91 	 $27,00 	 $27,00 	 $138,91 	aug 23–aug 30	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE				TRUE	
41	szett	https://www.ebay.com/itm/175805311641		 $148,08 	 $148,08 	 $8,69 	 $8,69 	 $156,77 	aug 28–szept 4	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE			TRUE	TRUE	
42	szett	https://www.ebay.com/itm/175832523070		 $122,56 	 $122,56 	 $11,46 	 $11,46 	 $134,02 	aug 28–szept 4	TRUE					TRUE	TRUE			TRUE		
43	szett	https://www.ebay.com/itm/185487611972		 $122,89 	 $122,89 	 $11,46 	 $11,46 	 $134,35 	aug 28–szept 4	TRUE					TRUE	TRUE					
44	szett	https://www.ebay.com/itm/254951373789		 $101,85 	 $101,85 	 $-   	 $-   	 $101,85 	aug 24–aug 31	TRUE					TRUE	TRUE			TRUE		
45	szett	https://www.ebay.com/itm/265154870750		 $159,99 	 $159,99 	 $-   	 $-   	 $159,99 	aug 28–szept 18	TRUE		TRUE	TRUE	TRUE	TRUE	TRUE				TRUE	
46	szett	https://www.ebay.com/itm/266362701794		 $102,98 	 $102,98 	 $-   	 $-   	 $102,98 	aug 30–szept 20	TRUE					TRUE	TRUE			TRUE		
47	szett	https://www.ebay.com/itm/275981481942		 $111,91 	 $111,91 	 $-   	 $-   	 $111,91 	aug 30–szept 20	TRUE					TRUE	TRUE			TRUE		
48	szett	https://www.ebay.com/itm/284732189871		 $180,25 	 $180,25 	 $8,69 	 $8,69 	 $188,94 	aug 28–szept 4	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE				TRUE	
49	szett	https://www.ebay.com/itm/284789595740		 $143,72 	 $143,72 	 $8,69 	 $8,69 	 $152,41 	aug 28–szept 4	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE			TRUE	TRUE	
50	szett	https://www.ebay.com/itm/284937098682		 $148,08 	 $148,08 	 $8,69 	 $8,69 	 $156,77 	aug 28–szept 4	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE	TRUE			TRUE	TRUE	
51	szett	https://www.ebay.com/itm/285356752268		 $123,32 	 $123,32 	 $31,41 	 $31,41 	 $154,73 	szept 4–szept 15	TRUE		TRUE			TRUE	TRUE					
52	szett	https://www.ebay.com/itm/285401626883		 $103,00 	 $103,00 	 $8,69 	 $8,69 	 $111,69 	aug 28–szept 4	TRUE			TRUE	TRUE	TRUE	TRUE			TRUE		
53	szett	https://www.ebay.com/itm/354229052638		 $121,59 	 $121,59 	 $3,00 	 $3,00 	 $124,59 	aug 28–szept 4	TRUE					TRUE	TRUE			TRUE		
54	szett	https://www.ebay.com/itm/384413634574	Simple Version Without GPS	 $114,19 	 $114,19 	 $7,00 	 $7,00 	 $121,19 	aug 24–aug 31	TRUE			TRUE		TRUE	TRUE					
55	szett	https://www.ebay.com/itm/384413634574	Standard Version Without GPS	 $122,28 	 $122,28 	 $7,00 	 $7,00 	 $129,28 	aug 24–aug 31	TRUE			TRUE	TRUE	TRUE	TRUE					
56	szett	https://www.ebay.com/itm/384413634574	Simple Version	 $155,25 	 $155,25 	 $7,00 	 $7,00 	 $162,25 	aug 24–aug 31	TRUE	TRUE		TRUE		TRUE	TRUE					
57	szett	https://www.ebay.com/itm/384413634574	Standard Version	 $174,95 	 $174,95 	 $7,00 	 $7,00 	 $181,95 	aug 24–aug 31	TRUE	TRUE		TRUE	TRUE	TRUE	TRUE					
58	szett	https://www.ebay.com/itm/385405633800		 $111,01 	 $111,01 	 $7,00 	 $7,00 	 $118,01 	aug 24–aug 31	TRUE					TRUE	TRUE					
59	szett	https://www.ebay.com/itm/404175469472		 $103,00 	 $103,00 	 $11,46 	 $11,46 	 $114,46 	aug 28–szept 4	TRUE			TRUE	TRUE	TRUE	TRUE			TRUE		
60	szett	https://www.ebay.com/itm/404386425612		 $104,12 	 $104,12 	 $-   	 $-   	 $104,12 	aug 30–szept 20	TRUE					TRUE	TRUE			TRUE		
61	ütődésvédő	https://www.ebay.com/itm/182717071164		 $5,59 	 $5,59 	 $3,89 	 $3,89 	 $9,48 	aug 18–aug 25											TRUE	
62	ütődésvédő	https://www.ebay.com/itm/264845165976		 $4,99 	 $4,99 	 $-   	 $-   	 $4,99 	szept 4–okt 2											TRUE	
63	ütődésvédő	https://www.ebay.com/itm/265166221718		 AUD6,59 	 $4,34 	 $-   	 $-   	 $4,34 	szept 4–okt 2											TRUE	
"""

raw_products = raw.split("\n") # split by newlines
raw_products = [x for x in raw_products if x.strip() != ""] # split by newlines, remove empty lines
raw_products = [x.split("\t") for x in raw_products] # split lines by tabs

# remove components: delivery date, PPM decoder, telemetry, pitot tube, SD card, LED+USB
raw_products = [(x[8], x[1], [*x[10:14], *x[15:17], x[20]]) for x in raw_products]

products_with_categories = [[float(p[0].strip()[1:].replace(",", ".")), p[1], *["TRUE" in x for x in p[2]]] for p in raw_products] # convert string to data types
products_with_categories = [(i + 1, *p) for i, p in enumerate(products_with_categories)] # add indices to products, split price and components
products = [(*p[0:2], p[3:]) for p in products_with_categories] # remove product category for finding combinations

print("Products:")
print("\n".join([f"{prod[0]}.\t${prod[1]}\t" + "\t".join([str(c) for c in prod[2]]) for prod in products]))

def get_top_combinations(products, combination_count = 1, price_cap = None, products_count_cap = None, verbosity_level = 0):
    # a combination is a tuple: (total price, [product indices])

    def leave_out_selected_components(prod, selected):
        def leave_out_selected_components_in_product(p):
            return (*p[0:2],
                    [component for i, component in enumerate(p[2]) if selected[i] == False]
                    )

        return [leave_out_selected_components_in_product(p) for p in prod]
    
    def leave_out_product_with_index(prod, index):
        return [p for i, p in enumerate(prod) if i != index]
    
    if not products:
        raise Exception("The products do not cover all components")
    
    def get_top_subcombinations(products, current_sum, product_count=0, logging_prefix=""):
        combinations = []
        for i in range(0, len(products)):
            product = products[i]
            current_product_price = product[1]

            # logging
            if product_count < verbosity_level:
                print(logging_prefix + str(i))

            # try to optimise by leaving out combinations with too big intermediate prices
            if price_cap and current_sum + current_product_price > price_cap:
                continue

            # try to optimise by leaving out combinations with too many products
            if products_count_cap and product_count > products_count_cap:
                continue
            
            current_selected_components = product[2]

            # if there are no more components that this product can add, skip it
            if not any(current_selected_components):
                continue

            # if there are no more components to select, simply add the product to the combinations
            if all(current_selected_components):
                combinations.append((current_product_price, [product[0]])) # price and index of product
                continue

            # get the combinations of the remaining components
            left_out_products = leave_out_product_with_index(products, i) # leave out the currently selected product for the rest
            left_out_products = leave_out_selected_components(left_out_products, current_selected_components) # consider only the components that have not yet been selected

            subcombinations = get_top_subcombinations(left_out_products, current_sum + current_product_price, product_count + 1, logging_prefix + f"{i}/")

            # merge the combinations with the current product
            for subcombination in subcombinations:
                selected_products = [product[0], *subcombination[1]]
                selected_products = sorted(selected_products, key=lambda x: x)
                combinations.append((current_product_price + subcombination[0], selected_products))
        
        # select the top combination_count combinations with the lowest total price, in ascending order
        combinations = [(sum([p[1] for p in products if p[0] in c]), list(c)) for c in list(set([tuple(cc[1]) for cc in combinations]))] # remove duplicate combinations

        return sorted(combinations, key=lambda x: x[0])[:combination_count]
    
    return get_top_subcombinations(products, current_sum=0)

def mergeCombinationsByProductCategories(combinations, products, dontMergeJustConvert = False):
    # turn combination tuples into merged combination tuples
    # a merged combination is a tuple: (min total price, max total price, [product indice groups])

    def getProductCategory(productIndex, dontCategoriseSets = False):
            category = [p[2] for p in products if p[0] == productIndex][0]

            if dontCategoriseSets or category != "szett":
                return category
            
            return "szett" + str(productIndex)
    
    combinationGroups = []

    while combinations:
        combination = combinations.pop(0)

        # find combinations that have the same component categories
        matchingCombinations = ([c for c in combinations
            if set([getProductCategory(p) for p in combination[1]]) == set([getProductCategory(p) for p in c[1]])]
            if not dontMergeJustConvert else [])
        
        combinations = [c for c in combinations if c not in matchingCombinations]
        combinationGroup = [combination, *matchingCombinations]
        combinationGroups.append(combinationGroup)

    # merge the combinations in each group
    def mergeCombinationsInGroup(combinations):
        subgroups = [[c] for c in combinations[0][1]]

        for combination in combinations[1:]:
            for component in combination[1]:
                category = getProductCategory(component)

                for subgroup in subgroups:
                    if category == getProductCategory(subgroup[0]) and component not in subgroup:
                        subgroup.append(component)
                        break

        subgroups = [sorted(s, key=lambda x: x) for s in subgroups]

        return subgroups

    return [(min([c[0] for c in g]),
             max([c[0] for c in g]),
             mergeCombinationsInGroup(g)) for g in combinationGroups]

top_combinations = None
if not use_parsed_combinations:
    top_combinations = get_top_combinations(products, combination_count=number_of_combinations or 10, price_cap=160, products_count_cap=5, verbosity_level=0)
    # print("\n".join([f"${c[0]:.0f}: {', '.join([str(cp) for cp in c[1]])}" for c in top_combinations]))
    # copy("\n".join([f"{c[0]}\t" + '\t'.join([str(cp) for cp in c[1]]) for c in top_combinations]))
else:
    # Using this list of combinations instead of the computed one from above
    top_combinations = """
    $133: 2, 24, 30, 66
    $134: 2, 24, 30, 65
    $134: 2, 25, 30, 66
    $134: 2, 26, 30, 66
    """

    top_combinations = top_combinations.split("\n")
    top_combinations = [tuple(c.split(": ")) for c in top_combinations if c != ""]
    top_combinations = [(float(c[0][1:]), [int(i) for i in c[1].split(", ")]) for c in top_combinations]

    print("Not recomputing combinations, using the list provided in the code instead.")

def printCombinations(merged_combinations):
    print("\n".join([f"${c[0]:.0f}–${c[1]:.0f}: " + '; '.join(["(" + ", ".join([str(ge) for ge in cp]) + ")" for cp in c[2]]) for c in merged_combinations]))

def formatCombinationsForClipboard(merged_combinations):
    maxGroupSize = 4
    return "\n".join([(f"{c[0]:.0f}\t{c[1]:.0f}\t" + '\t'.join(["\t".join([str(c) for c in [*cg, *[""] * maxGroupSize][:maxGroupSize]]) for cg in c[2]])) if c else "" for c in merged_combinations])

top_combinations_merged = mergeCombinationsByProductCategories(top_combinations, products_with_categories, dontMergeJustConvert)

print(f"\nBest combinations, {'unmerged' if dontMergeJustConvert else 'merged'}:")
printCombinations(top_combinations_merged)

clipboard = formatCombinationsForClipboard(top_combinations_merged)

if bothMergedAndUnmerged:
    top_combinations_unmerged = mergeCombinationsByProductCategories(top_combinations, products_with_categories, dontMergeJustConvert=True)

    print(f"\nBest combinations, unmerged:")
    printCombinations(top_combinations_unmerged)

    clipboard += "\n\n" + formatCombinationsForClipboard(top_combinations_unmerged)

copy(clipboard)
