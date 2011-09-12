package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class PromptState extends JSONObject
	{
		// Constructor
		public function PromptState(data:String, existingcontent:Object = null)
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
		public function Show():Boolean
		{
			return super.flash_proxy::getProperty("show");
		}
		public function Title():String
		{
			return super.flash_proxy::getProperty("title");
		}
		public function Text1():String
		{
			return super.flash_proxy::getProperty("text1");
		}
		public function Edit1():Boolean
		{
			return super.flash_proxy::getProperty("edit1");
		}
		public function Edit1Default():String
		{
			return super.flash_proxy::getProperty("edit1default");
		}
		public function Edit1Validation():String
		{
			return super.flash_proxy::getProperty("edit1validation");
		}
		public function Text2():String
		{
			return super.flash_proxy::getProperty("text2");
		}
		public function Edit2():Boolean
		{
			return super.flash_proxy::getProperty("edit2");
		}
		public function Edit2Default():String
		{
			return super.flash_proxy::getProperty("edit2default");
		}
		public function Edit2Validation():String
		{
			return super.flash_proxy::getProperty("edit2validation");
		}
		public function Buttons():Array
		{
			// Parse the buttons
			if (m_pButtons == null)
			{
				m_pButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("buttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pButtons.push(pButton);
				}
			}
			return m_pButtons;
		}
		
		// Type
		static public var TYPE:String = "promptstate";
		
		// State components
		private var m_pButtons:Array;
	}
}
