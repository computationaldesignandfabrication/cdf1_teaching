# Hyperbolic Crochet Making from Pseudo Code

Pick **one** of the two examples below and follow its pseudocode, stitch by stitch, to actually crochet the piece.

For instructions on specific crochet techniques referenced in the pseudocode (slipknot, chain stitch, slipstitch, double crochet, turning work, etc.), watch the videos here:
[Crochet technique videos (Google Drive)](https://drive.google.com/drive/folders/1fw-1CDxeuUIQ1zDhzpR52ZHCn_w4t_O_?usp=sharing)

---

## Example 1: Pseudosphere

![Pseudosphere](pseudosphere.png)

```
PROCEDURE CrochetPseudosphere()
    // 1. Start and make a base line
    current_layer = 0
    CALL make_a_starting_slipknot() // go to video for instructions

    FOR index = 1 TO 4
        CALL make_a_chain_stitch() // go to video for instructions
    END FOR

    // 2. Join to the first stitch to make a ring
    CALL make_a_slipstitch_to_first_chain()  // go to video for instructions

    // 3. Make 12 double crochets into the ring center
    current_stitches_in_round = 0
    FOR i = 1 TO 12
        CALL double_crochet_into_the_ring_center()
        current_stitches_in_round = current_stitches_in_round + 1
    END FOR
    current_layer = current_layer + 1

    // 4. Hyperbolic expansion in spiral: Make 3x double crochet to each stitch
    continue_pattern = TRUE
    WHILE continue_pattern = TRUE DO
        FOR s = 1 TO current_stitches_in_round
            FOR k = 1 TO 3
                CALL double_crochet_to_stitch() // go to video for instructions
            END FOR
        END FOR
        current_stitches_in_round = current_stitches_in_round * 3
        current_layer = current_layer + 1

        continue_pattern = check_if_continue()
    END WHILE

    CALL finish_pattern() // go to video for instructions 

END PROCEDURE
```

---

## Example 2: Hyperbolic Surface Ornament

![Hyperbolic surface](hyperbolic.png)

```
PROCEDURE CrochetHyperbolicSurfaceOrnament()
    // 1. Start and make base line
    current_layer = 0
    CALL make_a_starting_slipknot() // go to video for instructions

    current_stitches_in_line = 0
    FOR i = 1 TO 16
        CALL make_a_chain_stitch() // go to video for instructions
        current_stitches_in_line = current_stitches_in_line +1
    END FOR

    // 2. Hyperbolic expansion in rows: Make 2x double crochet to each stitch
    row_count = 3
    FOR r = 1 TO row_count
        FOR s = 1 TO current_stitches_in_line
            FOR k = 1 TO 2
                CALL double_crochet_in_line()
            END FOR
        END FOR
        current_stitches_in_line = current_stitches_in_line * 2
        current_layer = current_layer + 1

        CALL turn_work() 
    END FOR

    CALL finish_pattern()// go to video for instructions
    
END PROCEDURE
```
