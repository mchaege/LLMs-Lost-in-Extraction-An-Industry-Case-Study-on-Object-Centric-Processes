
import src.experiment as ex
import src.data_import as di




for setting in (
    ex.ExperimentSetting("gpt-5.5", ["naive"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive_ocel"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["algorithmic"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_algorithmic"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.non_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.non_chunker),

    ex.ExperimentSetting("gpt-5.5", ["naive"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive_ocel"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["algorithmic"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_algorithmic"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.section_chunker),
    ex.ExperimentSetting("gpt-5.5", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.section_chunker),


    ex.ExperimentSetting("claude-opus-4-6", ["naive"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive_ocel"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["algorithmic"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_algorithmic"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.non_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.non_chunker),

    ex.ExperimentSetting("claude-opus-4-6", ["naive"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive_ocel"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["algorithmic"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_algorithmic"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.section_chunker),


    ex.ExperimentSetting("gpt-5-nano", ["naive"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive_ocel"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["algorithmic"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_algorithmic"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.non_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.non_chunker),

    ex.ExperimentSetting("gpt-5-nano", ["naive"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive_ocel"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["algorithmic"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_algorithmic"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.section_chunker),


    ex.ExperimentSetting("claude-haiku-4-5", ["naive"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive_ocel"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["algorithmic"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_algorithmic"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_algorithmic_ocel"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.non_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.non_chunker),

    ex.ExperimentSetting("claude-haiku-4-5", ["naive"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive_ocel"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["algorithmic"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_algorithmic"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_algorithmic_ocel"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive_cascading_step_1_ocel", "improved_naive_cascading_step_2_ocel"], di.section_chunker),


    ex.ExperimentSetting("gpt-5.5", ["improved_algorithmic"], di.section_chunker),
    ex.ExperimentSetting("claude-opus-4-6", ["improved_algorithmic"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_algorithmic"], di.section_chunker),
    ex.ExperimentSetting("claude-haiku-4-5", ["improved_naive_cascading_step_1", "improved_naive_cascading_step_2"], di.section_chunker),
    ex.ExperimentSetting("gpt-5-nano", ["improved_algorithmic"], di.section_chunker),
):
        responses = ex.run_experiment(
                model_name=setting.model,
                prompt_variant_names=setting.prompt_variants,
                context_file_path=r"section_text.txt",
                chunking_func=setting.chunker,
                runs=5,
                show_token_usage=True,
        )