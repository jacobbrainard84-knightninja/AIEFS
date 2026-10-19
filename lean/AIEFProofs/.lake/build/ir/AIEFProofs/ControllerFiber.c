// Lean compiler output
// Module: AIEFProofs.ControllerFiber
// Imports: public import Init public meta import Init public import Mathlib.Algebra.BigOperators.Fin public import Mathlib.Data.Matrix.Basic public import Mathlib.Tactic.FinCases public import Mathlib.Tactic.Linarith
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* lp_mathlib_Nat_cast___at___00Mathlib_Tactic_Linarith_SimplexAlgorithm_postprocess_spec__0(lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
lean_object* l_Rat_neg(lean_object*);
static lean_once_cell_t lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0;
static lean_once_cell_t lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__1;
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___boxed(lean_object*, lean_object*);
static lean_once_cell_t lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___closed__0;
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl(lean_object*);
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___boxed(lean_object*);
static lean_object* _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0(void){
_start:
{
lean_object* v___x_1_; lean_object* v___x_2_; 
v___x_1_ = lean_unsigned_to_nat(1u);
v___x_2_ = lp_mathlib_Nat_cast___at___00Mathlib_Tactic_Linarith_SimplexAlgorithm_postprocess_spec__0(v___x_1_);
return v___x_2_;
}
}
static lean_object* _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__1(void){
_start:
{
lean_object* v___x_3_; lean_object* v___x_4_; 
v___x_3_ = lean_unsigned_to_nat(0u);
v___x_4_ = lp_mathlib_Nat_cast___at___00Mathlib_Tactic_Linarith_SimplexAlgorithm_postprocess_spec__0(v___x_3_);
return v___x_4_;
}
}
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl(lean_object* v_x_5_, lean_object* v_x_6_){
_start:
{
lean_object* v_zero_11_; uint8_t v_isZero_12_; 
v_zero_11_ = lean_unsigned_to_nat(0u);
v_isZero_12_ = lean_nat_dec_eq(v_x_5_, v_zero_11_);
if (v_isZero_12_ == 1)
{
uint8_t v_isZero_13_; 
v_isZero_13_ = lean_nat_dec_eq(v_x_6_, v_zero_11_);
if (v_isZero_13_ == 1)
{
goto v___jp_7_;
}
else
{
lean_object* v_one_14_; lean_object* v_n_15_; uint8_t v_isZero_16_; 
v_one_14_ = lean_unsigned_to_nat(1u);
v_n_15_ = lean_nat_sub(v_x_6_, v_one_14_);
v_isZero_16_ = lean_nat_dec_eq(v_n_15_, v_zero_11_);
if (v_isZero_16_ == 1)
{
lean_dec(v_n_15_);
goto v___jp_7_;
}
else
{
lean_object* v_n_17_; uint8_t v_isZero_18_; 
v_n_17_ = lean_nat_sub(v_n_15_, v_one_14_);
lean_dec(v_n_15_);
v_isZero_18_ = lean_nat_dec_eq(v_n_17_, v_zero_11_);
lean_dec(v_n_17_);
goto v___jp_9_;
}
}
}
else
{
lean_object* v_one_19_; lean_object* v_n_20_; uint8_t v_isZero_21_; uint8_t v_isZero_22_; 
v_one_19_ = lean_unsigned_to_nat(1u);
v_n_20_ = lean_nat_sub(v_x_5_, v_one_19_);
v_isZero_21_ = lean_nat_dec_eq(v_n_20_, v_zero_11_);
lean_dec(v_n_20_);
v_isZero_22_ = lean_nat_dec_eq(v_x_6_, v_zero_11_);
if (v_isZero_22_ == 1)
{
goto v___jp_7_;
}
else
{
lean_object* v_n_23_; uint8_t v_isZero_24_; 
v_n_23_ = lean_nat_sub(v_x_6_, v_one_19_);
v_isZero_24_ = lean_nat_dec_eq(v_n_23_, v_zero_11_);
if (v_isZero_24_ == 1)
{
lean_dec(v_n_23_);
goto v___jp_9_;
}
else
{
lean_object* v_n_25_; uint8_t v_isZero_26_; 
v_n_25_ = lean_nat_sub(v_n_23_, v_one_19_);
lean_dec(v_n_23_);
v_isZero_26_ = lean_nat_dec_eq(v_n_25_, v_zero_11_);
lean_dec(v_n_25_);
goto v___jp_7_;
}
}
}
v___jp_7_:
{
lean_object* v___x_8_; 
v___x_8_ = lean_obj_once(&lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0, &lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0_once, _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0);
return v___x_8_;
}
v___jp_9_:
{
lean_object* v___x_10_; 
v___x_10_ = lean_obj_once(&lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__1, &lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__1_once, _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__1);
return v___x_10_;
}
}
}
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___boxed(lean_object* v_x_27_, lean_object* v_x_28_){
_start:
{
lean_object* v_res_29_; 
v_res_29_ = lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl(v_x_27_, v_x_28_);
lean_dec(v_x_28_);
lean_dec(v_x_27_);
return v_res_29_;
}
}
static lean_object* _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___closed__0(void){
_start:
{
lean_object* v___x_30_; lean_object* v___x_31_; 
v___x_30_ = lean_obj_once(&lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0, &lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0_once, _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0);
v___x_31_ = l_Rat_neg(v___x_30_);
return v___x_31_;
}
}
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl(lean_object* v_x_32_){
_start:
{
lean_object* v_zero_35_; uint8_t v_isZero_36_; 
v_zero_35_ = lean_unsigned_to_nat(0u);
v_isZero_36_ = lean_nat_dec_eq(v_x_32_, v_zero_35_);
if (v_isZero_36_ == 1)
{
lean_object* v___x_37_; 
v___x_37_ = lean_obj_once(&lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0, &lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0_once, _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_CCtrl___closed__0);
return v___x_37_;
}
else
{
lean_object* v_one_38_; lean_object* v_n_39_; uint8_t v_isZero_40_; 
v_one_38_ = lean_unsigned_to_nat(1u);
v_n_39_ = lean_nat_sub(v_x_32_, v_one_38_);
v_isZero_40_ = lean_nat_dec_eq(v_n_39_, v_zero_35_);
if (v_isZero_40_ == 1)
{
lean_dec(v_n_39_);
goto v___jp_33_;
}
else
{
lean_object* v_n_41_; uint8_t v_isZero_42_; 
v_n_41_ = lean_nat_sub(v_n_39_, v_one_38_);
lean_dec(v_n_39_);
v_isZero_42_ = lean_nat_dec_eq(v_n_41_, v_zero_35_);
lean_dec(v_n_41_);
goto v___jp_33_;
}
}
v___jp_33_:
{
lean_object* v___x_34_; 
v___x_34_ = lean_obj_once(&lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___closed__0, &lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___closed__0_once, _init_lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___closed__0);
return v___x_34_;
}
}
}
LEAN_EXPORT lean_object* lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl___boxed(lean_object* v_x_43_){
_start:
{
lean_object* v_res_44_; 
v_res_44_ = lp_AIEFProofs_AIEFProofs_ControllerFiber_vCtrl(v_x_43_);
lean_dec(v_x_43_);
return v_res_44_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Algebra_BigOperators_Fin(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Data_Matrix_Basic(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Tactic_FinCases(uint8_t builtin);
lean_object* initialize_mathlib_Mathlib_Tactic_Linarith(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_AIEFProofs_AIEFProofs_ControllerFiber(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Algebra_BigOperators_Fin(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Data_Matrix_Basic(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Tactic_FinCases(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_mathlib_Mathlib_Tactic_Linarith(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
