// Page component for configuring application settings.
import { Box, Text, VStack, useToast } from "@chakra-ui/react";
import { useState, useEffect, useCallback } from "react";
import { settingsService } from "../utils/settings/settingsUtils";
import UserSettingsPanel from "../components/settings/UserSettingsPanel";
import ModelSettingsPanel from "../components/settings/ModelSettingsPanel";
import PromptSettingsPanel from "../components/settings/PromptSettingsPanel";
import RagSettingsPanel from "../components/settings/RagSettingsPanel";
import LetterTemplatesPanel from "../components/settings/LetterTemplatesPanel";
import SettingsActions from "../components/settings/SettingsActions";
import { SPECIALTIES } from "../utils/constants/index.js";
import TemplateSettingsPanel from "../components/settings/TemplateSettingsPanel";
import ChatSettingsPanel from "../components/settings/ChatSettingsPanel";
import { templateService } from "../utils/services/templateService";

const Settings = () => {
    const [userSettings, setUserSettings] = useState({
        name: "",
        specialty: "",
        quick_chat_1_title: "Critique my plan",
        quick_chat_1_prompt: "Critique my plan",
        quick_chat_2_title: "Any additional investigations",
        quick_chat_2_prompt: "Any additional investigations",
        quick_chat_3_title: "Any differentials to consider",
        quick_chat_3_prompt: "Any differentials to consider",
    });
    const [prompts, setPrompts] = useState(null);
    const [options, setOptions] = useState({
        general: { num_ctx: 0 },
        secondary: { num_ctx: 0 },
        letter: { temperature: 0 },
        reasoning: { num_ctx: 0, temperature: 0 },
    });
    const [templates, setTemplates] = useState({});
    const [letterTemplates, setLetterTemplates] = useState([]);

    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [modelOptions, setModelOptions] = useState([]);
    const [openaiModelOptions, setOpenAIModelOptions] = useState({ chat: [], embedding: [] });
    const [whisperModelOptions, setWhisperModelOptions] = useState([]);
    const [whisperModelListAvailable, setWhisperModelListAvailable] =
        useState(false);

    const toast = useToast();
    const [urlStatus, setUrlStatus] = useState({
        whisper: false,
        ollama: false,
        openai: false,
    });
    const [collapseStates, setCollapseStates] = useState({
        userSettings: false,
        modelSettings: true,
        promptSettings: true,
        ragSettings: true,
        letterTemplates: true,
        templates: true,
        chatSettings: true,
    });
    const fetchSettings = useCallback(async () => {
        try {
            setLoading(true);
            const configData = await settingsService.fetchConfig();
            setConfig(configData);

            await Promise.all([
                settingsService.fetchPrompts(setPrompts),
                settingsService.fetchOptions(setOptions),
                settingsService.fetchUserSettings(setUserSettings),
                settingsService.fetchTemplates(setTemplates),
            ]);

            // Fetch and merge default template into user settings
            const defaultTemplate = await templateService.getDefaultTemplate();
            setUserSettings((prev) => ({
                ...prev,
                default_template: defaultTemplate.template_key,
            }));

            // Fetch Ollama models if configured
            if (configData?.OLLAMA_BASE_URL) {
                await settingsService.fetchOllamaModels(
                    configData.OLLAMA_BASE_URL,
                    setModelOptions,
                );
            }

            // Fetch OpenAI models if configured
            if (configData?.OPENAI_API_KEY && configData?.OPENAI_API_KEY !== "&nbsp;" &&
                configData?.OPENAI_BASE_URL) {
                try {
                    const openaiModels = await settingsService.fetchOpenAIModels(
                        configData.OPENAI_BASE_URL,
                        configData.OPENAI_API_KEY
                    );
                    setOpenAIModelOptions(openaiModels.models);

                    // If we have OpenAI models, add them to the model options
                    if (openaiModels.models.chat && openaiModels.models.chat.length > 0) {
                        setModelOptions(prev => {
                            // Combine Ollama models with OpenAI models
                            const combined = [...prev, ...openaiModels.models.chat];
                            return combined;
                        });
                    }
                } catch (error) {
                    console.error("Error fetching OpenAI models:", error);
                }
            }

            if (configData?.WHISPER_BASE_URL) {
                await settingsService.fetchWhisperModels(
                    configData.WHISPER_BASE_URL,
                    setWhisperModelOptions,
                    setWhisperModelListAvailable,
                );
            }
        } catch (error) {
            console.error("Error loading settings:", error);
            toast({
                title: "Error loading settings",
                description: error.message,
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSettings();
    }, [fetchSettings]);

    useEffect(() => {
        const validateUrls = async () => {
            if (config?.WHISPER_BASE_URL) {
                const whisperValid = await settingsService.validateUrl(
                    "whisper",
                    config.WHISPER_BASE_URL,
                );
                setUrlStatus((prev) => ({ ...prev, whisper: whisperValid }));
            }

            if (config?.OLLAMA_BASE_URL) {
                const ollamaValid = await settingsService.validateUrl(
                    "ollama",
                    config.OLLAMA_BASE_URL,
                );
                setUrlStatus((prev) => ({ ...prev, ollama: ollamaValid }));
            }

            // Check OpenAI connection
            if (config?.OPENAI_API_KEY && config?.OPENAI_API_KEY !== "&nbsp;" &&
                config?.OPENAI_BASE_URL) {
                try {
                    // Use our backend API to validate the OpenAI connection
                    const apiUrl = `/api/config/openai/models?openaiEndpoint=${encodeURIComponent(config.OPENAI_BASE_URL)}&openaiKey=${encodeURIComponent(config.OPENAI_API_KEY)}`;
                    const response = await fetch(apiUrl);
                    setUrlStatus((prev) => ({ ...prev, openai: response.ok }));
                } catch (error) {
                    console.error("Error validating OpenAI connection:", error);
                    setUrlStatus((prev) => ({ ...prev, openai: false }));
                }
            }
        };

        validateUrls();
    }, [config?.WHISPER_BASE_URL, config?.OLLAMA_BASE_URL, config?.OPENAI_API_KEY, config?.OPENAI_BASE_URL]);

    useEffect(() => {
        const fetchLetterTemplates = async () => {
            try {
                const response = await settingsService.fetchLetterTemplates();
                setLetterTemplates(response.templates);

                if (response.default_template_id !== null) {
                    setUserSettings((prev) => ({
                        ...prev,
                        default_letter_template_id:
                            response.default_template_id,
                    }));
                }
            } catch (error) {
                console.error("Failed to fetch letter templates:", error);
            }
        };
        fetchLetterTemplates();
    }, []);

    const toggleCollapse = (section) => {
        setCollapseStates((prev) => ({
            ...prev,
            [section]: !prev[section],
        }));
    };

    const handleSaveChanges = async () => {
        try {
            await settingsService.saveSettings({
                prompts,
                config,
                options,
                userSettings,
                toast,
            });

            // Fetch settings again after saving
            await fetchSettings();

            toast({
                title: "Settings saved and refreshed",
                status: "success",
                duration: 3000,
                isClosable: true,
            });
        } catch (error) {
            toast({
                title: "Error saving settings",
                description: error.message,
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    const handleRestoreDefaults = async () => {
        await settingsService.resetToDefaults(fetchSettings, toast);
    };

    const handlePromptChange = (promptType, field, value) => {
        setPrompts((prev) => ({
            ...prev,
            [promptType]: {
                ...prev[promptType],
                [field]: value,
            },
        }));
    };

    const handleOptionChange = (category, key, value) => {
        setOptions((prev) => ({
            ...prev,
            [category]: {
                ...prev[category],
                [key]: value,
            },
        }));
    };
    const handleConfigChange = (key, value) => {
        // Update local config state only
        setConfig((prev) => ({
            ...prev,
            [key]: value,
        }));
    };

    const handleClearDatabase = async (newEmbeddingModel) => {
        await settingsService.clearDatabase(newEmbeddingModel, config, toast);
        // Refresh settings after database clear
        await fetchSettings();
    };

    if (loading) {
        return <Box>Loading...</Box>;
    }
    return (
        <Box p="5" borderRadius="sm" w="100%">
            <Text as="h2" mb="4">
                Settings
            </Text>
            <VStack spacing="5" align="stretch">
                <UserSettingsPanel
                    isCollapsed={collapseStates.userSettings}
                    setIsCollapsed={() => toggleCollapse("userSettings")}
                    userSettings={userSettings}
                    setUserSettings={setUserSettings}
                    specialties={SPECIALTIES}
                    templates={templates}
                    letterTemplates={letterTemplates}
                    toast={toast}
                />

                <ModelSettingsPanel
                    isCollapsed={collapseStates.modelSettings}
                    setIsCollapsed={() => toggleCollapse("modelSettings")}
                    config={config}
                    handleConfigChange={handleConfigChange}
                    modelOptions={modelOptions}
                    whisperModelOptions={whisperModelOptions}
                    whisperModelListAvailable={whisperModelListAvailable}
                    urlStatus={urlStatus}
                />

                <PromptSettingsPanel
                    isCollapsed={collapseStates.promptSettings}
                    setIsCollapsed={() => toggleCollapse("promptSettings")}
                    prompts={prompts}
                    handlePromptChange={handlePromptChange}
                    options={options}
                    handleOptionChange={handleOptionChange}
                    config={config}
                />

                <RagSettingsPanel
                    isCollapsed={collapseStates.ragSettings}
                    setIsCollapsed={() => toggleCollapse("ragSettings")}
                    config={config}
                    modelOptions={modelOptions}
                    openaiModelOptions={openaiModelOptions}
                    handleClearDatabase={handleClearDatabase}
                    handleConfigChange={handleConfigChange}
                />

                <TemplateSettingsPanel
                    isCollapsed={collapseStates.templates}
                    setIsCollapsed={() => toggleCollapse("templates")}
                    templates={templates}
                    setTemplates={setTemplates}
                />

                <LetterTemplatesPanel
                    isCollapsed={collapseStates.letterTemplates}
                    setIsCollapsed={() => toggleCollapse("letterTemplates")}
                />

                <ChatSettingsPanel
                    isCollapsed={collapseStates.chatSettings}
                    setIsCollapsed={() => toggleCollapse("chatSettings")}
                    userSettings={userSettings}
                    setUserSettings={setUserSettings}
                />

                <SettingsActions
                    onSave={handleSaveChanges}
                    onRestoreDefaults={handleRestoreDefaults}
                />
            </VStack>
        </Box>
    );
};

export default Settings;
