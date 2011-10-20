package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class RunState extends JSONObject
	{
		// Constructor
		public function RunState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Username():String
		{
			return super.flash_proxy::getProperty("username");
		}
		public function Status():String
		{
			return super.flash_proxy::getProperty("status");
		}
		public function SequenceID():uint
		{
			return super.flash_proxy::getProperty("sequenceid");
		}
		public function ComponentID():uint
		{
			return super.flash_proxy::getProperty("componentid");
		}
		public function PromptState():Elixys.Objects.PromptState
		{
			// Parse the prompt state
			if (m_pPromptState == null)
			{
				m_pPromptState = new Elixys.Objects.PromptState(null, super.flash_proxy::getProperty("prompt"));
			}
			return m_pPromptState;
		}
		
		// Type
		static public var TYPE:String = "runstate";

		// State components
		private var m_pPromptState:Elixys.Objects.PromptState;
	}
}