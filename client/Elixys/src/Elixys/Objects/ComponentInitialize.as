package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentInitialize extends Component
	{
		// Constructor
		public function ComponentInitialize(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			return "";
		}

		// Type
		static public var TYPE:String = "INITIALIZE";

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"INITIALIZE\"," +
			"\"id\":0," +
			"\"name\":\"Initialize\"}";
	}
}
